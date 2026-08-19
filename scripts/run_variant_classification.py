# -*- coding: utf-8 -*-
"""
run_variant_classification.py — LLM 变异致病性分类实验

用途：对 ClinVar 采样变异的记录，调用 LLM 做 ACMG/AMP 致病性分类，
      记录分类结果 + 证据 + 引用，供与 ClinGen/ClinVar 金标准对照。

核心设计（与论文大纲一致）：
    - 时间盲法：测试集只含训练截止后提交的变异（preprocess_clinvar.py 产出）
    - 多模型：DeepSeek 全量 + GPT/Claude/Gemini 子集
    - 记录：分类、置信度、引用、耗时、成本（RQ5）

复用：
    - 软件工程项目的 call_llm（同一 DeepSeek API 基建）
    - .env 自动加载（含 API key）

依赖：标准库 + requests（项目已有）

使用：
    python run_variant_classification.py --input data/clinvar_testset.csv --model deepseek-v4-pro --limit 100
    python run_variant_classification.py --input data/clinvar_testset.csv --models deepseek-v4-pro,deepseek-chat
    python run_variant_classification.py --dry-run --limit 5   # 调试 prompt
"""
import os
import sys
import csv
import json
import time
import argparse
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# call_llm 复用模块（本项目 scripts/ 内，不依赖外部项目）
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

DATA_DIR = HERE.parent / "data"
RESULTS_DIR = HERE.parent / "results"
OUT_CSV = DATA_DIR / "variant_classification_results.csv"

from call_llm import call_llm, _has_api_key
LLM_AVAILABLE = True

# ACMG/AMP 致病性分类标签（模型输出应落到这些类）
ACMG_CLASSES = [
    "Pathogenic", "Likely pathogenic", "Uncertain significance",
    "Likely benign", "Benign",
]


def build_variant_prompt(variant: dict, af_mode: str = "auto") -> str:
    """
    构造 ACMG 分类 prompt。
    输入变异记录 → 输出：分类 + 依据的 ACMG 规则 + 参考文献（用于 RQ4 引用验证）。

    af_mode（AF 对照实验用）：
      - auto：有 AF 列且非空则加入
      - on：  强制加入（无值则注明缺失）
      - off： 强制不加（无 AF 基线，主实验默认）
    """
    name = variant.get("Name", "")          # 如 NM_000059.3:c.123A>G
    gene = variant.get("GeneSymbol", "")
    chrm = variant.get("Chromosome", "")
    start = variant.get("Start", "")
    ref = variant.get("ReferenceAllele", "")
    alt = variant.get("AlternateAllele", "")
    hgvs_c = variant.get("HGVS_cDNA", "")
    hgvs_p = variant.get("HGVS_Protein", "")

    # 人群频率（AF 对照实验：clinvar_testset_af.csv 由 annotate_af.py 产出）
    afs = []
    for k, label in (("AF_ESP", "ESP"), ("AF_EXAC", "ExAC"), ("AF_TGP", "1000G")):
        v = str(variant.get(k, "") or "").strip()
        if v and v.lower() not in ("na", "none"):
            afs.append(f"{label}={v}")
    has_af = bool(afs)
    af_block = ""
    if af_mode == "on" or (af_mode == "auto" and has_af):
        af_block = (f"Population allele frequencies (ACMG BA1/BS1/PM2 evidence):\n"
                    f"{'; '.join(afs) if afs else 'not available in source database'}\n")

    prompt = (
        "You are a clinical geneticist. Classify the pathogenicity of the following "
        "genetic variant according to the ACMG/AMP 2015 guidelines.\n"
        f"\nVariant: {name or 'N/A'}\n"
        f"Gene: {gene or 'N/A'}\n"
        f"Genomic: chr{chrm}:{start} {ref}>{alt}\n"
        f"HGVS cDNA: {hgvs_c or 'N/A'}\n"
        f"HGVS protein: {hgvs_p or 'N/A'}\n"
        f"{af_block}"
        "\nOutput STRICTLY in this JSON format (no extra text):\n"
        '{"classification": "Pathogenic|Likely pathogenic|Uncertain significance|'
        'Likely benign|Benign",\n'
        ' "acmg_rules": ["PVS1", "PS1", ...],\n'
        ' "confidence": 0.0-1.0,\n'
        ' "evidence_summary": "one sentence",\n'
        ' "references": ["author, journal, year, ..."]}\n'
    )
    return prompt


def parse_llm_json(output: str) -> dict:
    """
    从 LLM 输出解析 JSON。容忍：```json 围栏、前后杂文本、单引号。
    解析失败返回 {"classification": "", "parse_error": 输出前200字符}。
    """
    if not output:
        return {"classification": "", "parse_error": "empty output"}
    # 剥围栏
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", output, re.S)
    text = m.group(1) if m else output
    # 找第一个 { 到最后一个 }
    s, e = text.find("{"), text.rfind("}")
    if s < 0 or e <= s:
        return {"classification": "", "parse_error": text[:200]}
    try:
        return json.loads(text[s:e + 1])
    except json.JSONDecodeError:
        # 单引号容忍
        try:
            fixed = re.sub(r"(?<!\\)'", '"', text[s:e + 1])
            return json.loads(fixed)
        except json.JSONDecodeError:
            return {"classification": "", "parse_error": text[s:e + 1][:200]}


def classify_class(parsed: dict) -> str:
    """把模型输出的 classification 归一到 ACMG 5 类。"""
    raw = str(parsed.get("classification", "")).strip().lower()
    for c in ACMG_CLASSES:
        if c.lower() == raw or c.lower() in raw:
            return c
    return "other"  # 模型输出了非标准类


def main():
    ap = argparse.ArgumentParser(description="LLM 变异致病性分类实验")
    ap.add_argument("--input", default=str(DATA_DIR / "clinvar_testset.csv"),
                    help="变异输入 CSV（preprocess_clinvar 产出）")
    ap.add_argument("--models", default="deepseek-v4-pro",
                    help="逗号分隔模型列表")
    ap.add_argument("--limit", type=int, default=None, help="只跑前 N 个变异（调试）")
    ap.add_argument("--dry-run", action="store_true", help="只打印 prompt 不调用")
    ap.add_argument("--out", default=str(OUT_CSV), help="结果 CSV")
    ap.add_argument("--workers", type=int, default=4,
                    help="并发线程数（v4-pro 每次调用 40-100s，建议 4-8）")
    ap.add_argument("--resume", action="store_true",
                    help="断点续跑：跳过输出 CSV 中已完成的 (AlleleID, model)")
    ap.add_argument("--timeout", type=int, default=900,
                    help="单次任务外部超时（秒，超时记为 error 不中断整体）")
    ap.add_argument("--af-mode", default="auto",
                    choices=["auto", "on", "off"],
                    help="AF 对照：auto=有AF列则带 / on=强制带 / off=强制不带")
    ap.add_argument("--system-all", action="store_true",
                    help="稳健性检验：国内模型也加研究性 system prompt")
    args = ap.parse_args()

    if not LLM_AVAILABLE:
        sys.exit("✗ 无法 import 软件工程项目的 call_llm，请确认路径正确")

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if not args.dry_run:
        missing = [m for m in models if not _has_api_key(m)]
        if missing:
            sys.exit(f"✗ 缺少 API key: {missing}")

    if not Path(args.input).exists():
        sys.exit(f"✗ 找不到 {args.input}，请先运行 preprocess_clinvar.py")

    # 读变异记录
    variants = []
    with Path(args.input).open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            variants.append(row)
    if args.limit:
        variants = variants[: args.limit]
    print(f"加载 {len(variants)} 个变异 × {len(models)} 模型 "
          f"= {len(variants) * len(models)} 次分类")

    # 结果文件
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 断点续跑：收集已完成 (AlleleID, model)
    # ⚠️ resume 必须以追加模式打开（"w" 会覆盖清空已有结果！）
    # ⚠️ error 行不视为完成（网关超时等失败调用需重试）
    done = set()
    need_header = True
    if args.resume and out_path.exists():
        good_rows = []
        n_err = 0
        with out_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                aid, m = row.get("AlleleID", ""), row.get("model", "")
                if row.get("llm_class") == "error":
                    n_err += 1
                    continue
                if aid and m:
                    done.add((aid, m))
                    good_rows.append(row)
        if n_err > 0:
            # 重写文件：只保留成功行，error 行将重新执行
            tmp = out_path.with_suffix(".csv.tmp")
            with tmp.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(good_rows)
            tmp.replace(out_path)
            print(f"续跑模式：清除 {n_err} 条 error 行（将重试），"
                  f"跳过 {len(done)} 条成功记录")
        else:
            print(f"续跑模式：已跳过 {len(done)} 条成功记录")
        need_header = False  # 文件已有表头，追加时不重复写

    # 任务清单
    tasks = []
    for var in variants:
        aid = var.get("AlleleID", "")
        for model in models:
            if (aid, model) in done:
                continue
            tasks.append((var, model))
    print(f"待执行: {len(tasks)} 条")

    if args.dry_run:
        for var, model in tasks[:5]:
            print(f"\n--- {var.get('AlleleID')} / {model} (DRY) ---")
            print(build_variant_prompt(var))
        print(f"\n（dry-run 仅展示前 5 条，共 {len(tasks)} 条）")
        return

    f_out = out_path.open("a" if args.resume and out_path.exists()
                          else "w", encoding="utf-8", newline="")
    writer = csv.writer(f_out)
    if need_header:
        writer.writerow(["AlleleID", "GeneSymbol", "model", "prompt_class",
                         "llm_class", "confidence", "acmg_rules",
                         "references", "parse_error", "time_s",
                         "notes"])

    def work(item):
        """单次分类任务（线程内执行）。返回 (行, 错误或None)。"""
        var, model = item
        t0 = time.time()
        try:
            # 推理模型（deepseek-v4* / mimo* / qwen* / glm* / kimi*）：思考+输出共享
            # max_tokens 预算，需调高（1024 会被 reasoning 耗尽导致 content 为空）
            # 国际模型走中转（gemini/gpt-5/claude），实测需 16384（002 项目同配置）
            if model.startswith(("gemini", "gpt-5", "claude")):
                mt = 16384
            elif model.startswith(("deepseek-v4", "mimo", "qwen", "glm",
                                   "kimi")):
                mt = 8192
            else:
                mt = 1024
            # 国际模型（走中转）加研究性 system prompt：Claude 会对纯临床
            # 任务触发医疗安全拒答（实测 5/20），研究语境声明可消除；
            # 三家国外模型统一加，Methods 如实披露（国内模型无 system）
            # --system-all：稳健性检验用，国内模型也加同一 system prompt
            system = None
            if model.startswith(("gemini", "gpt-5", "claude")) or args.system_all:
                system = ("You are participating in a research benchmark that "
                          "evaluates language models on ACMG/AMP 2015 germline "
                          "variant classification using public ClinVar-style "
                          "records. Classifications are research outputs, not "
                          "clinical advice. Respond with the required JSON only.")
            output = call_llm(model, build_variant_prompt(var, args.af_mode),
                              max_tokens=mt, system=system)
            elapsed = round(time.time() - t0, 2)
            parsed = parse_llm_json(output)
            return ([var.get("AlleleID", ""), var.get("GeneSymbol", ""),
                     model, var.get("ClinicalSignificance", ""),
                     classify_class(parsed),
                     parsed.get("confidence", ""),
                     ";".join(parsed.get("acmg_rules", []) or []),
                     ";".join(parsed.get("references", []) or []),
                     parsed.get("parse_error", ""),
                     elapsed, ""], None)
        except Exception as e:  # noqa: BLE001
            elapsed = round(time.time() - t0, 2)
            return ([var.get("AlleleID", ""), var.get("GeneSymbol", ""),
                     model, var.get("ClinicalSignificance", ""),
                     "error", "", "", "", "", elapsed, str(e)[:100]], e)

    n_done = 0
    n_error = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, t): t for t in tasks}
        for fut in as_completed(futs):
            try:
                row, err = fut.result(timeout=args.timeout + 60)
            except Exception as e:  # 外部超时等：拿不到结果，记 error 行
                var, model = futs[fut]
                row = [var.get("AlleleID", ""), var.get("GeneSymbol", ""),
                       model, var.get("ClinicalSignificance", ""),
                       "error", "", "", "", "", "",
                       f"外部超时(>{args.timeout}s)"]
                err = e
            writer.writerow(row)
            f_out.flush()
            if err:
                n_error += 1
                print(f"  ✗ {row[0]}/{row[2]}: "
                      f"{type(err).__name__}: {str(err)[:80]}",
                      file=sys.stderr)
            else:
                n_done += 1
                if n_done % 50 == 0:
                    print(f"  ... {n_done} 完成")

    f_out.close()
    print(f"\n完成: {n_done} / 失败 {n_error}")
    print(f"结果: {out_path}")


if __name__ == "__main__":
    main()
