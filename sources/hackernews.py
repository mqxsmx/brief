"""Hacker News 数据源:取 front_page 热门帖(algolia API)。

HN 无官方 Trending,用 algolia 搜索 API(tags=front_page + 时间窗口 + points 门槛)。
输出 Project:title 作 name,url 外链(Ask/Show HN 无 url 则用 HN 帖子页),
HN 专属字段(points/num_comments/author/created_at/story_text)走 extra。
"""
from __future__ import annotations
import time
import requests

from core.registry import register_source
from core.base import Source
from core.models import Project

HN_API = "https://hn.algolia.com/api/v1/search"
HN_ITEM_URL = "https://news.ycombinator.com/item?id="


@register_source("hackernews")
class HackerNews(Source):
    """params:
      hits_per_page: 从 API 取多少条(过滤前)
      min_points: 最低票数门槛(质量过滤)
      window_hours: 时间窗口(过去 N 小时),日报取近 24h
    """

    def __init__(self, hits_per_page: int = 30, min_points: int = 50, window_hours: int = 24):
        self.hits_per_page = hits_per_page
        self.min_points = min_points
        self.window_hours = window_hours

    def fetch(self) -> list[Project]:
        cutoff = int(time.time()) - self.window_hours * 3600
        params = {
            "tags": "front_page",
            "hitsPerPage": self.hits_per_page,
            "numericFilters": f"created_at_i>{cutoff},points>{self.min_points}",
        }
        r = requests.get(
            HN_API, params=params,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Brief/0.1)"},
            timeout=30,
        )
        r.raise_for_status()
        hits = r.json().get("hits", [])
        # 按 points 降序(高票优先)
        hits.sort(key=lambda h: h.get("points", 0), reverse=True)
        return [self._to_project(h) for h in hits]

    @staticmethod
    def _to_project(h: dict) -> Project:
        title = h.get("title", "") or ""
        url = h.get("url") or (HN_ITEM_URL + str(h.get("objectID", "")))
        story_text = h.get("story_text", "") or ""
        return Project(
            name=title,
            url=url,
            description=story_text or title,
            source="hackernews",
            extra={
                "points": h.get("points", 0),
                "num_comments": h.get("num_comments", 0),
                "author": h.get("author", ""),
                "created_at": h.get("created_at", ""),
                "hn_id": h.get("objectID", ""),
                "story_text": story_text,
            },
        )
