#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本快照：每次反馈迭代自动归档，支持版本对比与回滚。

为什么有这个脚本（竞品对比 v3 的 P1 升级）：
  学 paper-ppt-agent 的「版本历史管理」—— 每次反馈迭代自动归档快照，
  支持版本对比与回溯。解决的实际问题：
  「改了几轮之后想回到上一版」在手工流程里做不到。

子命令：
    save     归档当前版本（PPTX + 可选 manifest + 备注）
    list     列出所有历史版本
    restore  回滚到指定版本（把归档复制回工作路径）
    diff     对比两个版本（复用 zip 逐文件比较）

用法：
    python scripts/snapshot.py save    --deck output.pptx --note "初稿"
    python scripts/snapshot.py list
    python scripts/snapshot.py restore --version 20261012-093800 --to output.pptx
    python scripts/snapshot.py diff    --a v1.pptx --b v2.pptx

归档目录（默认）：<deck 同级>/iterations/
    iterations/
    ├── 20261012-093800/
    │   ├── output.pptx
    │   ├── meta.json       （时间、备注、来源）
    │   └── slide_manifest.json（若提供）
    └── index.json          （全部版本索引）

安全设计（防"改崩"）：
    - restore 默认**不覆盖**已存在的文件，需 --force
    - restore 前自动把当前文件另存一份（.before-restore）
    - 所有操作只增不删，不留孤儿
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def get_iter_dir(deck: Path, base: Path | None) -> Path:
    d = base if base else deck.parent / "iterations"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_index(iter_dir: Path) -> list[dict]:
    idx = iter_dir / "index.json"
    if idx.exists():
        try:
            return json.loads(idx.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_index(iter_dir: Path, items: list[dict]) -> None:
    (iter_dir / "index.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ---------------------------------------------------------------------------


def cmd_save(args) -> int:
    deck = Path(args.deck)
    if not deck.exists():
        print(f"[FAIL] 文件不存在: {deck}")
        return 1

    iter_dir = get_iter_dir(deck, Path(args.dir) if args.dir else None)
    ts = args.version or time.strftime("%Y%m%d-%H%M%S")
    vdir = iter_dir / ts
    if vdir.exists() and not args.force:
        print(f"[FAIL] 版本已存在: {ts}（加 --force 覆盖）")
        return 1
    vdir.mkdir(parents=True, exist_ok=True)

    # 归档 PPTX
    target = vdir / deck.name
    shutil.copy2(deck, target)

    # 归档 manifest（若提供）
    if args.manifest and Path(args.manifest).exists():
        shutil.copy2(args.manifest, vdir / "slide_manifest.json")

    # 元数据
    meta = {
        "version": ts,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": args.note or "",
        "source": str(deck),
        "file": deck.name,
        "size_bytes": deck.stat().st_size,
    }
    (vdir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 更新索引
    items = load_index(iter_dir)
    items = [x for x in items if x.get("version") != ts]
    items.append(meta)
    items.sort(key=lambda x: x.get("version", ""))
    save_index(iter_dir, items)

    print(f"✅ 已归档版本: {ts}")
    print(f"   目录: {vdir}")
    if args.note:
        print(f"   备注: {args.note}")
    return 0


def cmd_list(args) -> int:
    deck = Path(args.deck) if args.deck else None
    if not deck:
        print("[FAIL] list 需要 --deck 定位归档目录")
        return 1
    iter_dir = get_iter_dir(deck, Path(args.dir) if args.dir else None)
    items = load_index(iter_dir)
    if not items:
        print(f"暂无历史版本（归档目录: {iter_dir}）")
        return 0
    print(f"历史版本（{len(items)} 个，归档目录: {iter_dir}）")
    print("=" * 60)
    for x in items:
        note = f" — {x['note']}" if x.get("note") else ""
        size = x.get("size_bytes", 0)
        print(f"  {x['version']}  ({size/1024:.0f} KB){note}")
    return 0


def cmd_restore(args) -> int:
    deck = Path(args.deck)
    iter_dir = get_iter_dir(deck, Path(args.dir) if args.dir else None)
    vdir = iter_dir / args.version
    if not vdir.exists():
        print(f"[FAIL] 版本不存在: {args.version}")
        print(f"   可用版本见: python scripts/snapshot.py list --deck <file>")
        return 1

    # 找到归档的 pptx
    meta_p = vdir / "meta.json"
    if meta_p.exists():
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        src = vdir / meta.get("file", "")
    else:
        src = vdir / deck.name
    if not src.exists():
        cands = list(vdir.glob("*.pptx")) + list(vdir.glob("*.pptm"))
        if not cands:
            print(f"[FAIL] 归档目录里没有 pptx: {vdir}")
            return 1
        src = cands[0]

    dst = Path(args.to) if args.to else deck
    if dst.exists() and not args.force:
        print(f"[FAIL] 目标已存在: {dst}（加 --force 覆盖）")
        return 1

    # 覆盖前先备份当前文件（防改崩）
    if dst.exists():
        bak = dst.with_suffix(dst.suffix + ".before-restore")
        shutil.copy2(dst, bak)
        print(f"   已备份当前文件: {bak}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"✅ 已回滚到版本 {args.version}")
    print(f"   {src} -> {dst}")
    return 0


def cmd_diff(args) -> int:
    a, b = Path(args.a), Path(args.b)
    for p in (a, b):
        if not p.exists():
            print(f"[FAIL] 文件不存在: {p}")
            return 1
    try:
        with zipfile.ZipFile(a) as za, zipfile.ZipFile(b) as zb:
            na, nb = set(za.namelist()), set(zb.namelist())
            added = sorted(nb - na)
            removed = sorted(na - nb)
            changed = [n for n in sorted(na & nb) if za.read(n) != zb.read(n)]
            print(f"版本对比: {a.name}  vs  {b.name}")
            print("=" * 60)
            print(f"  新增文件: {len(added)}")
            print(f"  删除文件: {len(removed)}")
            print(f"  变更文件: {len(changed)}")
            if changed:
                print("\n变更明细（前 10）:")
                for n in changed[:10]:
                    print(f"    - {n}")
    except zipfile.BadZipFile:
        print("[FAIL] 其中一个不是有效的 pptx")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="duduppt 版本快照管理")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_save = sub.add_parser("save", help="归档当前版本")
    p_save.add_argument("--deck", required=True)
    p_save.add_argument("--note", default="", help="版本备注")
    p_save.add_argument("--manifest", help="一并归档 slide_manifest.json")
    p_save.add_argument("--version", help="指定版本号（默认时间戳）")
    p_save.add_argument("--dir", help="归档根目录（默认 <deck同级>/iterations）")
    p_save.add_argument("--force", action="store_true")
    p_save.set_defaults(func=cmd_save)

    p_list = sub.add_parser("list", help="列出历史版本")
    p_list.add_argument("--deck", required=True)
    p_list.add_argument("--dir")
    p_list.set_defaults(func=cmd_list)

    p_restore = sub.add_parser("restore", help="回滚到指定版本")
    p_restore.add_argument("--deck", required=True)
    p_restore.add_argument("--version", required=True)
    p_restore.add_argument("--to", help="输出路径（默认覆盖原 deck）")
    p_restore.add_argument("--dir")
    p_restore.add_argument("--force", action="store_true")
    p_restore.set_defaults(func=cmd_restore)

    p_diff = sub.add_parser("diff", help="对比两个版本")
    p_diff.add_argument("--a", required=True)
    p_diff.add_argument("--b", required=True)
    p_diff.set_defaults(func=cmd_diff)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
