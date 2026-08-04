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

# 复用软件工程项目的 DeepSeek 基建（call_llm / .env 加载）
SE_PROJECT = Path(__file__).parent.parent.parent / "SCI_Paper_Project"
SE_SCRIPTS = SE_PROJECT / "study" / "scripts"
if SE_SCRIPTS.exists():
    sys.path.insert(0, str(SE_SCRIPTS))

HERE = Path(__file__).parent
DATA_DIR = HERE.parent / "data"
RESULTS_DIR = HERE.parent / "results"
OUT_CSV = DATA_DIR / "variant_classification_results.csv"

# 引入 call_llm（若软件工程项目可用）
try:
    from run_experiment import call_llm, _has_api_key  # noqa: E402
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# ACMG/AMP 致病性分类标签（模型输出应落到这些类）
ACMG_CLASSES = [
    "Pathogenic", "Likely pathogenic", "Uncertain significance",
    "Likely benign", "Benign",
]


def build_variant_prompt(variant: dict) -> str:
    """
    构造 ACMG 分类 prompt。
    输入变异记录 → 输出：分类 + 依据的 ACMG 规则 + 参考文献（用于 RQ4 引用验证）。
    """
    name = variant.get("Name", "")          # 如 NM_000059.3:c.123A>G
    gene = variant.get("GeneSymbol", "")
    chrm = variant.get("Chromosome", "")
    start = variant.get("Start", "")
    ref = variant.get("ReferenceAllele", "")
    alt = variant.get("AlternateAllele", "")
    hgvs_c = variant.get("HGVS_cDNA", "")
    hgvs_p = variant.get("HGVS_Protein", "")
    # 当前 ClinVar variant_summary 无 gnomAD AF 列；人群频率需另查 gnomAD API
    # （本实验首版不含 AF，论文中作为局限声明；后续可加 gnomAD 查询）

    prompt = (
        "You are a clinical geneticist. Classify the pathogenicity of the following "
        "genetic variant according to the ACMG/AMP 2015 guidelines.\n"
        f"\nVariant: {name or 'N/A'}\n"
        f"Gene: {gene or 'N/A'}\n"
        f"Genomic: chr{chrm}:{start} {ref}>{alt}\n"
        f"HGVS cDNA: {hgvs_c or 'N/A'}\n"
        f"HGVS protein: {hgvs_p or 'N/A'}\n"
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
    f_out = out_path.open("w", encoding="utf-8", newline="")
    writer = csv.writer(f_out)
    writer.writerow(["AlleleID", "GeneSymbol", "model", "prompt_class",
                     "llm_class", "confidence", "acmg_rules",
                     "references", "parse_error", "time_s",
                     "notes"])

    n_done = 0
    n_error = 0
    for i, var in enumerate(variants, 1):
        aid = var.get("AlleleID", "")
        gene = var.get("GeneSymbol", "")
        for model in models:
            prompt = build_variant_prompt(var)
            if args.dry_run:
                print(f"\n--- {aid} / {model} (DRY) ---")
                print(prompt)
                continue
            t0 = time.time()
            try:
                # v4 系列推理模型：思考+输出共享 max_tokens 预算，需调高
                # （1024 会被 reasoning 耗尽导致 content 为空，实测 8192 足够）
                mt = 8192 if model.startswith("deepseek-v4") else 1024
                output = call_llm(model, prompt, max_tokens=mt)
                elapsed = round(time.time() - t0, 2)
                parsed = parse_llm_json(output)
                cls = classify_class(parsed)
                writer.writerow([
                    aid, gene, model,
                    var.get("ClinicalSignificance", ""),
                    cls,
                    parsed.get("confidence", ""),
                    ";".join(parsed.get("acmg_rules", []) or []),
                    ";".join(parsed.get("references", []) or []),
                    parsed.get("parse_error", ""),
                    elapsed, ""
                ])
                f_out.flush()
                n_done += 1
                print(f"  [{i}/{len(variants)}] ✓ {aid}/{model}: "
                      f"{cls} ({elapsed}s)")
            except Exception as e:  # noqa: BLE001
                n_error += 1
                print(f"  [{i}/{len(variants)}] ✗ {aid}/{model}: "
                      f"{type(e).__name__}: {str(e)[:80]}", file=sys.stderr)
                writer.writerow([aid, gene, model,
                                 var.get("ClinicalSignificance", ""),
                                 "error", "", "", "", "", "", str(e)[:100]])
                f_out.flush()

    f_out.close()
    print(f"\n完成: {n_done} / 失败 {n_error}")
    print(f"结果: {out_path}")


if __name__ == "__main__":
    main()
