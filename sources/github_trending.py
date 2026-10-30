"""GitHub Trending 数据源:爬取 trending 页面。

注意:GitHub 无官方 Trending API,依赖页面 HTML 结构;
若页面改版导致解析失效,需更新下方选择器(已用注释标明定位)。
"""
from __future__ import annotations
import re
import requests
from bs4 import BeautifulSoup

from brief.registry import register_source
from brief.base import Source
from brief.models import Project

TRENDING_URL = "https://github.com/trending"


def _to_int(s: str) -> int:
    s = re.sub(r"[^\d]", "", s or "")
    return int(s) if s else 0


@register_source("github_trending")
class GitHubTrending(Source):
    """params:
      since: daily | weekly | monthly
      language: None(全语言) 或 'python' / 'go' / ...
    """

    def __init__(self, since: str = "daily", language: str | None = None):
        self.since = since
        self.language = language

    def fetch(self) -> list[Project]:
        params = {"since": self.since}
        if self.language:
            params["l"] = self.language
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Brief/0.1)"}
        resp = requests.get(TRENDING_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        items: list[Project] = []
        for article in soup.select("article.Box-row"):           # 每个项目卡片
            h2 = article.select_one("h2 a")
            if not h2:
                continue
            href = h2.get("href", "").split("?")[0].strip("/")
            name = "/".join(href.split("/")[:2])                  # owner/repo
            url = "https://github.com/" + name

            p = article.select_one("p")
            desc = p.get_text(strip=True) if p else ""

            lang_el = article.select_one("span[itemprop='programmingLanguage']")
            lang = lang_el.get_text(strip=True) if lang_el else ""

            # 总 star:指向 /stargazers 的链接
            total = 0
            for a in article.select("a"):
                if a.get("href", "").endswith("/stargazers"):
                    total = _to_int(a.get_text())
                    break

            # 今日新增 star:通常是 span.Float / .d-inline-block
            today = 0
            today_el = article.select_one("span.d-inline-block.float-sm-right") \
                or article.select_one("span.float-sm-right")
            if today_el:
                today = _to_int(today_el.get_text())

            items.append(Project(
                name=name, url=url, description=desc, language=lang,
                stars_total=total, stars_today=today, source="github_trending",
            ))
        return items
