"""第 1 层:硬过滤 —— 剔除确定的水项目。

保守原则:只删明确的(空描述 + 关键词黑名单),模糊判断交给后面评分。
fork / archived 在 quality_gate(有 API 数据)里处理。
"""
from __future__ import annotations
from brief.registry import register_processor
from brief.base import Processor

# 默认黑名单:资源汇总 / 模板 / 面试 / 教程 类,不算「项目」
DEFAULT_KEYWORDS = [
    "awesome", "interview", "面试", "leetcode", "resume", "简历",
    "template", "starter", "boilerplate", "course", "教程", "tutorial",
    "demo", "hello-world", "book", "资源", "list",
]


@register_processor("hard_filter")
class HardFilter(Processor):
    def __init__(self, keywords: list[str] | None = None, drop_no_desc: bool = True):
        self.keywords = [k.lower() for k in (keywords if keywords is not None else DEFAULT_KEYWORDS)]
        self.drop_no_desc = drop_no_desc

    def process(self, projects):
        out = []
        for p in projects:
            reason = None
            if self.drop_no_desc and not p.description:
                reason = "空描述"
            else:
                text = (p.name + " " + p.description).lower()
                hit = next((k for k in self.keywords if k in text), None)
                if hit:
                    reason = f"关键词:{hit}"
            if reason:
                p.extra["drop_reason"] = reason
            else:
                out.append(p)
        return out
