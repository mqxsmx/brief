"""加载并校验 config.yaml(简报清单)。"""
from __future__ import annotations
import os
from pathlib import Path
import yaml


def load_config(path: str | os.PathLike = "config.yaml") -> dict:
    """读公共 config.yaml(defaults)+ 扫描 briefs/<brief>/config.yaml(各 brief)。

    各 brief 配置继承 defaults(brief 同名字段覆盖,浅合并)。
    返回 {"briefs": [...], "defaults": {...}}。
    """
    base = Path(path)
    if not base.exists():
        raise FileNotFoundError(f"config 不存在: {base.resolve()}")
    root = yaml.safe_load(base.read_text(encoding="utf-8")) or {}
    defaults = root.get("defaults", {})

    briefs = []
    briefs_dir = base.parent / "briefs"
    if briefs_dir.is_dir():
        for bf in sorted(briefs_dir.iterdir()):
            if not bf.is_dir():
                continue
            bc = bf / "config.yaml"
            if not bc.exists():
                continue
            cfg = yaml.safe_load(bc.read_text(encoding="utf-8")) or {}
            if "name" not in cfg:
                cfg["name"] = bf.name
            briefs.append({**defaults, **cfg})  # brief 覆盖 defaults

    if not briefs:
        raise ValueError(f"未在 {briefs_dir} 下找到任何 brief 配置")
    return {"briefs": briefs, "defaults": defaults}


def find_brief(cfg: dict, name: str) -> dict:
    for b in cfg["briefs"]:
        if b.get("name") == name:
            return b
    available = ", ".join(b.get("name", "?") for b in cfg["briefs"])
    raise KeyError(f"未找到简报: {name}; 可用: {available}")
