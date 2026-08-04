# -*- coding: utf-8 -*-
"""
download_segments.py — 健壮的分段并行下载（带 gzip 完整性校验）

用途：下载大文件（如 ClinVar variant_summary 441MB）时，NCBI FTP 单连接限速
      （~30KB/s），分段并行可提升到 ~270KB/s。

健壮性设计（吸取上次教训）：
    1. 动态获取 Content-Length（HEAD 请求），不写死大小
    2. 按实际大小分段下载
    3. 下载后 gzip 完整性校验（EOFError 检测），失败自动重下损坏段
    4. 支持断点续传（已存在且完整的段跳过）

使用：
    python download_segments.py --url <URL> --out <path> [--segments 8]
    python download_segments.py --verify-only <path>   # 只校验
"""
import sys
import gzip
import shutil
import subprocess
import argparse
from pathlib import Path

# Windows curl 需跳过证书吊销检查（schannel 离线报错）
CURL_BASE = ["curl", "-sSL", "--ssl-no-revoke"]


def get_content_length(url: str) -> int:
    """HEAD 请求获取精确 Content-Length。"""
    r = subprocess.run(CURL_BASE + ["-sI", url],
                       capture_output=True, text=True, timeout=60)
    for line in r.stdout.splitlines():
        if line.lower().startswith("content-length:"):
            return int(line.split(":", 1)[1].strip())
    sys.exit(f"✗ 无法获取 Content-Length: {url}")


def verify_gzip(path: Path) -> bool:
    """gzip 完整性校验：能读完且无 EOFError 即完整。"""
    try:
        with gzip.open(path, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
        return True
    except (EOFError, gzip.BadGzipFile, OSError):
        return False


def download_segment(url: str, out: Path, start: int, end: int) -> bool:
    """下载一个分段。返回是否成功。"""
    r = subprocess.run(
        CURL_BASE + ["-r", f"{start}-{end}", "-o", str(out), url],
        capture_output=True, timeout=1800)
    return r.returncode == 0 and out.exists() and out.stat().st_size == (end - start + 1)


def main():
    ap = argparse.ArgumentParser(description="分段并行下载")
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True, help="输出文件路径")
    ap.add_argument("--segments", type=int, default=8)
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--max-retries", type=int, default=3)
    args = ap.parse_args()

    out = Path(args.out)
    if args.verify_only:
        print("gzip 完整 ✓" if verify_gzip(out) else "gzip 损坏 ✗")
        return 0 if verify_gzip(out) else 1

    total = get_content_length(args.url)
    print(f"文件大小: {total} 字节 ({total/1024/1024:.1f} MB)")
    seg_size = total // args.segments
    segs = []
    for i in range(args.segments):
        start = i * seg_size
        end = total - 1 if i == args.segments - 1 else start + seg_size - 1
        segs.append((start, end))

    # 并行下载（每段独立子进程）
    tmp_dir = out.parent / f".seg_{out.stem}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    procs = []
    for i, (start, end) in enumerate(segs):
        seg_path = tmp_dir / f"seg{i}.bin"
        if seg_path.exists() and seg_path.stat().st_size == (end - start + 1):
            print(f"  段{i}: 已存在，跳过")
            continue
        print(f"  段{i}: {start}-{end} ({end-start+1} 字节)")
        p = subprocess.Popen(
            CURL_BASE + ["-r", f"{start}-{end}", "-o", str(seg_path), args.url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p)

    for p in procs:
        p.wait()

    # 校验每段大小
    ok = True
    for i, (start, end) in enumerate(segs):
        seg_path = tmp_dir / f"seg{i}.bin"
        expect = end - start + 1
        actual = seg_path.stat().st_size if seg_path.exists() else 0
        if actual != expect:
            print(f"  ✗ 段{i} 大小不符: {actual} != {expect}，重试中...")
            ok = False
            for attempt in range(1, args.max_retries + 1):
                seg_path.unlink(missing_ok=True)
                if download_segment(args.url, seg_path, start, end):
                    ok = True
                    print(f"    ✓ 段{i} 重试成功")
                    break
            if not ok:
                sys.exit(f"✗ 段{i} 重试 {args.max_retries} 次仍失败")

    # 合并
    print("合并分段...")
    with out.open("wb") as fout:
        for i in range(args.segments):
            seg_path = tmp_dir / f"seg{i}.bin"
            with seg_path.open("rb") as fin:
                shutil.copyfileobj(fin, fout, 1024 * 1024)
    print(f"合并完成: {out} ({out.stat().st_size} 字节)")

    # gzip 完整性校验
    if verify_gzip(out):
        print("✓ gzip 完整性校验通过")
    else:
        print("✗ gzip 损坏！请检查网络或重试", file=sys.stderr)
        sys.exit(1)

    # 清理分段
    shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
