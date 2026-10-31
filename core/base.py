"""四个抽象基类:约定连接器接口。"""
from __future__ import annotations
from .models import Project, Digest


class Source:
    """数据源连接器:只负责取数据,输出标准化 Project 列表。"""
    def fetch(self) -> list[Project]:
        raise NotImplementedError


class Processor:
    """处理器:接收并返回 Project 列表,链式执行。"""
    def process(self, projects: list[Project]) -> list[Project]:
        raise NotImplementedError


class Renderer:
    """渲染器:把 Digest 转成最终内容字符串(HTML/Markdown/...)。"""
    def render(self, digest: Digest) -> str:
        raise NotImplementedError


class Channel:
    """投递渠道:把简报标题 + 内容发送出去。"""
    def send(self, subject: str, content: str) -> None:
        raise NotImplementedError
