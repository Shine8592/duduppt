#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duduppt Python 包。

说明：duduppt 的核心是 **Agent Skill**（SKILL.md + reference 文档 + 脚本），
本包的作用是把它作为**可分发的单元**发布到 PyPI，并提供 CLI
把 Skill 安装到各 Agent 的 skills 目录。

安装后：
    duduppt install            # 安装 Skill 到自动探测的 Agent
    duduppt install --agent claude / codex / cursor / opencode
    duduppt path               # 打印 Skill 在包内的路径

设计原则：核心依赖为零（Skill 本体是 Markdown），
各 Python 脚本所需依赖放在 optional-dependencies 里按需安装。
"""

__version__ = "3.2.0"

from pathlib import Path

# Skill 在包内的目录（由 setuptools package-data 打包进来）
SKILL_DIR = Path(__file__).resolve().parent / "skill"


def skill_path() -> Path:
    """返回包内 Skill 根目录；不存在则抛出可读错误。"""
    if not SKILL_DIR.exists():
        raise FileNotFoundError(
            f"包内未找到 skill 目录：{SKILL_DIR}（安装可能不完整，请重新安装 duduppt）"
        )
    return SKILL_DIR
