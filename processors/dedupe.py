"""第 6 层:去重。

本次实现单次运行内去重(按 name/url),跨多源聚合时去重同一项目。
跨天持久化(避免同一项目连续多天推送)留 TODO:
  可用 state.json + workflow 跑完 git commit 回推,或 GitHub Actions cache。
"""
from __future__ import annotations
from core.registry import register_processor
from core.base import Processor


@register_processor("dedupe")
class Dedupe(Processor):
    def process(self, projects):
        seen = set()
        out = []
        for p in projects:
            k = p.key
            if k in seen:
                continue
            seen.add(k)
            out.append(p)
        return out
