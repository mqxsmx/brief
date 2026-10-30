"""控制台渠道:打印到 stdout,用于本地调试。

config 里 channels 加 { type: console } 即可在本地看渲染结果,不发邮件。
"""
from __future__ import annotations
from brief.registry import register_channel
from brief.base import Channel


@register_channel("console")
class ConsoleChannel(Channel):
    def __init__(self, subject_prefix: str = "[Brief]"):
        self.subject_prefix = subject_prefix

    def send(self, subject: str, content: str) -> None:
        import sys
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        print("=" * 64)
        print(f"{self.subject_prefix} {subject}".strip())
        print("-" * 64)
        print(content)
        print("=" * 64)
