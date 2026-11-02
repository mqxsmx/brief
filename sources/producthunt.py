"""Product Hunt 数据源:取每日新品(PH Atom feed)。

PH 官方 GraphQL API 需 token;Atom feed(https://www.producthunt.com/feed)免费、无认证,
含 title/tagline/link/author/published(无 votes)。按 published 过滤近 N 小时,取 Top。
输出 Project:产品名作 name,tagline 作 description,元数据(author/published/ph_id/tagline)走 extra。
"""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import requests

from core.registry import register_source
from core.base import Source
from core.models import Project

PH_FEED = "https://www.producthunt.com/feed"
PH_NS = {"atom": "http://www.w3.org/2005/Atom"}


@register_source("producthunt")
class ProductHunt(Source):
    """params:
      window_hours: 只取近 N 小时发布的产品
      top_n: 取多少条
    """

    def __init__(self, window_hours: int = 24, top_n: int = 20):
        self.window_hours = window_hours
        self.top_n = top_n

    def fetch(self) -> list[Project]:
        r = requests.get(
            PH_FEED,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Brief/0.1)"},
            timeout=30,
        )
        r.raise_for_status()
        root = ET.fromstring(r.text)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.window_hours)
        out = []
        for entry in root.findall("atom:entry", PH_NS):
            published = entry.findtext("atom:published", default="", namespaces=PH_NS) or ""
            try:
                pdt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            except Exception:
                continue
            if pdt < cutoff:
                continue
            out.append(self._to_project(entry, published))
        # RSS 无 votes,按发布时间倒序(最新在前)
        out.sort(key=lambda p: p.extra.get("published", ""), reverse=True)
        return out[: self.top_n]

    @staticmethod
    def _to_project(entry, published: str) -> Project:
        title = (entry.findtext("atom:title", default="", namespaces=PH_NS) or "").strip()
        link = ""
        for l in entry.findall("atom:link", PH_NS):
            if l.get("rel") == "alternate":
                link = l.get("href", "")
                break
        content = entry.findtext("atom:content", default="", namespaces=PH_NS) or ""
        # tagline = content 里第一个 <p> 的纯文本
        m = re.search(r"<p[^>]*>\s*(.*?)\s*</p>", content, re.S)
        tagline = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
        author = entry.findtext("atom:author/atom:name", default="", namespaces=PH_NS) or ""
        id_text = entry.findtext("atom:id", default="", namespaces=PH_NS) or ""
        ph_id = ""
        m2 = re.search(r"Post/(\d+)", id_text)
        if m2:
            ph_id = m2.group(1)
        return Project(
            name=title,
            url=link,
            description=tagline or title,
            source="producthunt",
            extra={
                "tagline": tagline,
                "author": author,
                "published": published,
                "ph_id": ph_id,
            },
        )
