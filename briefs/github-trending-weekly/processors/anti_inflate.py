"""第 3 层:反刷榜 —— 基于 star 与其他指标背离检测可疑膨胀。

实现已有数据能算的:fork-star 比、当日增量占比。
star-history 曲线检测(垂直暴涨=刷榜)留 TODO。
默认标记可疑(score_rank 据此降权),不直接删 —— 宁可漏不可错。
"""
from __future__ import annotations
from core.registry import register_processor
from core.base import Processor


@register_processor("anti_inflate")
class AntiInflate(Processor):
    def __init__(self, min_fork_star_ratio: float = 0.008,
                 max_today_ratio: float = 0.5,
                 suspect_stars_threshold: int = 500,
                 drop_suspect: bool = False):
        self.min_ratio = min_fork_star_ratio
        self.max_today_ratio = max_today_ratio
        self.suspect_stars = suspect_stars_threshold
        self.drop_suspect = drop_suspect

    def process(self, projects):
        out = []
        for p in projects:
            flags = []
            ratio = (p.forks / p.stars_total) if p.stars_total else 0.0
            today_ratio = (p.stars_today / p.stars_total) if p.stars_total else 0.0
            if p.stars_total > self.suspect_stars and ratio < self.min_ratio:
                flags.append(f"fork-star比低({ratio:.4f})")
            if p.stars_total > 200 and today_ratio > self.max_today_ratio:
                flags.append(f"当日增量占比高({today_ratio:.1%})")
            # TODO: 拉 star-history 曲线,垂直暴涨 → 刷榜;平滑上升 → 真实

            if flags:
                p.extra["inflate_flagged"] = True
                p.extra["inflate_reasons"] = flags
                if self.drop_suspect:
                    p.extra["drop_reason"] = "刷榜可疑:" + ";".join(flags)
                    continue
            out.append(p)
        return out
