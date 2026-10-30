"""加载并校验 config.yaml(简报清单)。"""
from __future__ import annotations
import os
from pathlib import Path
import yaml


def load_config(path: str | os.PathLike = "config.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"config 不存在: {p.resolve()}")
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not cfg or "briefs" not in cfg:
        raise ValueError("config.yaml 必须包含 briefs 列表")
    return cfg


def find_brief(cfg: dict, name: str) -> dict:
    for b in cfg["briefs"]:
        if b.get("name") == name:
            return b
    available = ", ".join(b.get("name", "?") for b in cfg["briefs"])
    raise KeyError(f"未找到简报: {name}; 可用: {available}")
