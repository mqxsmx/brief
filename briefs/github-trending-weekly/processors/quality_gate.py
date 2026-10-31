"""第 2 层:质量门槛 —— 调 GitHub API 补全元数据并卡阈值。

调 GET /repos/{owner}/{repo} 拿 forks/watchers/issues/license/created/pushed/topics;
通过基本检查后才取 README(省 API 配额),并存前 N 字符供 ai_filter 使用。
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
import requests

from core.registry import register_processor
from core.base import Processor

API = "https://api.github.com/repos/"


@register_processor("quality_gate")
class QualityGate(Processor):
    def __init__(self, min_forks: int = 5, min_watchers: int = 3,
                 min_readme_chars: int = 200, min_age_days: int = 3,
                 max_stale_days: int = 365, require_license: bool = False,
                 readme_excerpt_chars: int = 1500):
        self.min_forks = min_forks
        self.min_watchers = min_watchers
        self.min_readme_chars = min_readme_chars
        self.min_age_days = min_age_days
        self.max_stale_days = max_stale_days
        self.require_license = require_license
        self.readme_excerpt_chars = readme_excerpt_chars
        self.token = os.environ.get("GITHUB_TOKEN", "")
        self._info_cache: dict[str, dict | None] = {}

    def _headers(self, accept: str):
        h = {"Accept": accept}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _repo_info(self, name: str):
        if name in self._info_cache:
            return self._info_cache[name]
        try:
            r = requests.get(API + name, headers=self._headers("application/vnd.github+json"), timeout=15)
            info = r.json() if r.status_code == 200 else None
        except requests.RequestException:
            info = None
        self._info_cache[name] = info
        return info

    def _readme(self, name: str) -> str:
        try:
            r = requests.get(API + name + "/readme", headers=self._headers("application/vnd.github.raw"), timeout=15)
            return r.text if r.status_code == 200 else ""
        except requests.RequestException:
            return ""

    def process(self, projects):
        now = datetime.now(timezone.utc)
        out = []
        for p in projects:
            info = self._repo_info(p.name)
            if not info:
                p.extra["drop_reason"] = "API 获取失败"
                continue

            # 补全元数据
            p.forks = info.get("forks_count", 0)
            p.watchers = info.get("subscribers_count", 0)
            p.open_issues = info.get("open_issues_count", 0)
            p.created_at = info.get("created_at", "")
            p.pushed_at = info.get("pushed_at", "")
            p.license = (info.get("license") or {}).get("spdx_id", "") or ""
            p.topics = info.get("topics", []) or []

            if info.get("archived"):
                p.extra["drop_reason"] = "已归档"; continue
            if info.get("fork"):
                p.extra["drop_reason"] = "fork 项目"; continue

            # 基本检查(不依赖 README)
            reason = self._check_basic(p, now)
            if reason:
                p.extra["drop_reason"] = reason
                continue

            # 通过基本检查才取 README(省配额),并存摘要供 ai_filter 用
            readme = self._readme(p.name)
            p.readme_chars = len(readme)
            p.has_readme = p.readme_chars > 0
            p.readme_excerpt = readme[: self.readme_excerpt_chars]
            if p.readme_chars < self.min_readme_chars:
                p.extra["drop_reason"] = f"README 过短({p.readme_chars}<{self.min_readme_chars})"
                continue

            out.append(p)
        return out

    def _check_basic(self, p, now):
        if p.forks < self.min_forks:
            return f"forks 不足({p.forks}<{self.min_forks})"
        if p.watchers < self.min_watchers:
            return f"watchers 不足({p.watchers}<{self.min_watchers})"
        if self.require_license and not p.license:
            return "无 license"
        try:
            created = datetime.fromisoformat(p.created_at.replace("Z", "+00:00"))
            age = (now - created).days
            if age < self.min_age_days:
                return f"创建太近({age}d<{self.min_age_days})"
        except Exception:
            pass
        try:
            pushed = datetime.fromisoformat(p.pushed_at.replace("Z", "+00:00"))
            stale = (now - pushed).days
            if stale > self.max_stale_days:
                return f"长期未更新({stale}d)"
        except Exception:
            pass
        return None
