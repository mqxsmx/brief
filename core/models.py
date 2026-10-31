"""统一数据契约:所有 Source 产出、所有 Processor 处理、Renderer 渲染的对象。"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Project:
    name: str
    url: str
    description: str = ""
    language: str = ""
    stars_total: int = 0
    stars_today: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    created_at: str = ""
    pushed_at: str = ""
    license: str = ""
    has_readme: bool = False
    readme_chars: int = 0
    topics: list = field(default_factory=list)
    contributors: int = 0
    source: str = ""
    summary_cn: str = ""
    highlights: list = field(default_factory=list)        # AI 生成的价值亮点(中文)
    editor_note: str = ""                                  # AI 生成的编辑点评(一句话)
    readme_excerpt: str = ""                               # README 前 N 字符(供 AI 用)
    extra: dict = field(default_factory=dict)   # 过滤标记/原因,便于调参

    @property
    def key(self) -> str:
        """去重用键:仓库全名或 url。"""
        return self.name or self.url


@dataclass
class Digest:
    """一份简报的最终产物。"""
    date: str
    title: str
    projects: list[Project] = field(default_factory=list)
    meta: dict = field(default_factory=dict)
