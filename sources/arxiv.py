"""arXiv 数据源:取 cs.AI/cs.LG/cs.CL 每日新论文(arXiv Atom API)。

arXiv API 免费、无认证。按 submittedDate 倒序取最新 N 篇。
输出 Project:title 作 name,abstract 作 description,论文元数据(authors/published/category/arxiv_id)走 extra。
"""
from __future__ import annotations
import xml.etree.ElementTree as ET
import requests

from core.registry import register_source
from core.base import Source
from core.models import Project

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


@register_source("arxiv")
class Arxiv(Source):
    """params:
      categories: 逗号分隔的 arXiv 分类(默认 cs.AI,cs.LG,cs.CL)
      max_results: 取多少篇(过滤前)
    """

    def __init__(self, categories: str = "cs.AI,cs.LG,cs.CL", max_results: int = 30):
        self.categories = categories
        self.max_results = max_results

    def fetch(self) -> list[Project]:
        cat_query = "+OR+".join(f"cat:{c}" for c in self.categories.split(",") if c.strip())
        params = {
            "search_query": cat_query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(self.max_results),
        }
        r = requests.get(
            ARXIV_API, params=params,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Brief/0.1)"},
            timeout=30,
        )
        r.raise_for_status()
        root = ET.fromstring(r.text)
        return [self._to_project(e) for e in root.findall("atom:entry", ARXIV_NS)]

    @staticmethod
    def _to_project(entry) -> Project:
        title = " ".join((entry.findtext("atom:title", default="", namespaces=ARXIV_NS) or "").split())
        summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ARXIV_NS) or "").split())
        url = ""
        for link in entry.findall("atom:link", ARXIV_NS):
            if link.get("rel") == "alternate":
                url = link.get("href", "")
                break
        if not url:
            url = entry.findtext("atom:id", default="", namespaces=ARXIV_NS) or ""
        authors = [a.findtext("atom:name", default="", namespaces=ARXIV_NS) for a in entry.findall("atom:author", ARXIV_NS)]
        published = entry.findtext("atom:published", default="", namespaces=ARXIV_NS) or ""
        category = ""
        pc = entry.find("{http://arxiv.org/schemas/atom}primary_category")
        if pc is not None:
            category = pc.get("term", "")
        arxiv_id = url.rsplit("/", 1)[-1] if url else ""
        return Project(
            name=title or arxiv_id,
            url=url,
            description=summary,
            source="arxiv",
            extra={
                "authors": authors[:10],
                "published": published,
                "category": category,
                "arxiv_id": arxiv_id,
            },
        )
