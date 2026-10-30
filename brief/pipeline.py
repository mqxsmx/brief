"""编排器:按一份 brief 配置跑完整链路。

Source(可多源聚合) → Processor 链 → Renderer → Channel(可多渠道)。
纯配置驱动,主干零改动即可扩展。
"""
from __future__ import annotations
from datetime import datetime
from .models import Project, Digest
from .registry import SOURCES, PROCESSORS, RENDERERS, CHANNELS


def _inst(registry: dict[str, type], item: dict):
    """从 config 的一项 {type, params} 实例化插件。"""
    cls = registry[item["type"]]
    return cls(**(item.get("params") or {}))


def run(brief_cfg: dict) -> Digest:
    # 1. 取数据(可多源聚合)
    projects: list[Project] = []
    for s in brief_cfg.get("sources", []):
        projects += _inst(SOURCES, s).fetch()

    # 2. 处理器链(过滤 / 去重 / 打分 / 可选 AI)
    for p in brief_cfg.get("processors", []):
        projects = _inst(PROCESSORS, p).process(projects)

    # 3. 渲染
    digest = Digest(
        date=datetime.now().strftime("%Y-%m-%d"),
        title=brief_cfg.get("title", brief_cfg.get("name", "Brief")),
        projects=projects,
    )
    content = _inst(RENDERERS, brief_cfg["renderer"]).render(digest)

    # 4. 投递(可多渠道)
    for c in brief_cfg.get("channels", []):
        _inst(CHANNELS, c).send(digest.title, content)

    return digest
