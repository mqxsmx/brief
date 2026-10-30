"""第 4 层:综合评分排序,取 Top N。可疑项降权。"""
from __future__ import annotations
from brief.registry import register_processor
from brief.base import Processor
from brief.models import Project


@register_processor("score_rank")
class ScoreRank(Processor):
    def __init__(self, top_n: int = 15, inflate_penalty: float = 0.5):
        self.top_n = top_n
        self.inflate_penalty = inflate_penalty

    @staticmethod
    def _norm(v: float, cap: float) -> float:
        return min(v / cap, 1.0) if cap else 0.0

    def _score(self, p: Project) -> float:
        s = (
            0.25 * self._norm(p.forks, 500) +
            0.15 * self._norm(p.open_issues, 100) +
            0.15 * self._norm(p.readme_chars, 5000) +
            0.10 * (1.0 if p.license else 0.0) +
            0.10 * self._norm(len(p.topics), 10) +
            0.15 * self._norm(p.stars_today, 500) +
            0.10 * self._norm(p.watchers, 500)
        )
        if p.extra.get("inflate_flagged"):
            s *= self.inflate_penalty
        return s

    def process(self, projects):
        scored = sorted(projects, key=self._score, reverse=True)
        return scored[: self.top_n]
