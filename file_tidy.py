#!/usr/bin/env python3
"""file-tidy —— 把乱糟糟的文件夹按扩展名归类。

用法：
    python file_tidy.py 目标文件夹             # 真的移动文件
    python file_tidy.py 目标文件夹 --dry-run   # 只打印，不动手
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# 扩展名 -> 分类文件夹名。想加新类型，直接在这里加一行就行。
CATEGORIES: dict[str, set[str]] = {
    "图片": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"},
    "文档": {".pdf", ".doc", ".docx", ".txt", ".md", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"},
    "压缩包": {".zip", ".rar", ".7z", ".tar", ".gz", ".xz"},
    "音视频": {".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav", ".flac", ".m4a"},
    "代码": {".py", ".c", ".h", ".cpp", ".js", ".ts", ".html", ".css", ".java", ".go", ".rs"},
    "安装包": {".exe", ".msi", ".dmg", ".apk", ".deb"},
}


def category_of(path: Path) -> str:
    """根据扩展名判断它该进哪个文件夹，认不出来的归到「其他」。"""
    suffix = path.suffix.lower()
    for name, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return name
    return "其他"


def plan(target: Path) -> list[tuple[Path, Path]]:
    """算出「原路径 -> 新路径」的清单，全程不碰任何文件。"""
    moves: list[tuple[Path, Path]] = []
    for item in sorted(target.iterdir()):
        if not item.is_file():          # 只处理文件，跳过已经分好的文件夹
            continue
        if item.name.startswith("."):   # 跳过隐藏文件
            continue
        dest_dir = target / category_of(item)
        dest = dest_dir / item.name
        n = 1
        while dest.exists():            # 重名就加序号，绝不覆盖
            dest = dest_dir / f"{item.stem}_{n}{item.suffix}"
            n += 1
        moves.append((item, dest))
    return moves


def main() -> int:
    parser = argparse.ArgumentParser(description="把文件夹里的文件按扩展名整理")
    parser.add_argument("target", nargs="?", default=".", help="要整理的文件夹，默认当前目录")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不真的移动")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"这不是一个文件夹：{target}")
        return 1

    moves = plan(target)
    if not moves:
        print("没有需要整理的文件，已经很整齐了。")
        return 0

    for src, dest in moves:
        print(f"  {src.name:<32} -> {dest.parent.name}/")
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))

    verb = "将会移动" if args.dry_run else "已移动"
    print(f"\n{verb} {len(moves)} 个文件。")
    if args.dry_run:
        print("（演练模式：文件没动。去掉 --dry-run 才会真的整理。）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
