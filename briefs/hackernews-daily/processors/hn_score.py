"""HN 评分排序:按 points + comments 综合排序取 Top N。

points 为主,comments 加权(讨论热度)。HN 无 forks/stars,用社区投票数 + 评论数衡量热度。
"""
from __future__ import annotations
from core.registry import register_processor
from core.base import Processor


@register_processor("hn_score")
class HnScore(Processor):
    def __init__(self, top_n: int = 20, comment_weight: float = 0.5):
        self.top_n = top_n
        self.comment_weight = comment_weight

    def process(self, projects):
        def score(p):
            pts = p.extra.get("points", 0)
            cmt = p.extra.get("num_comments", 0)
            return pts + cmt * self.comment_weight
        scored = sorted(projects, key=score, reverse=True)
        return scored[: self.top_n]
