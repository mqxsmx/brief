"""HTML 渲染器:用 Jinja2 模板把 Digest 转成 HTML 邮件。"""
from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.registry import register_renderer
from core.base import Renderer
from core.models import Digest


@register_renderer("html")
class HtmlRenderer(Renderer):
    def __init__(self, template: str = ""):
        if not template:
            raise ValueError("html renderer 需在 config 的 renderer.params 指定 template 路径")
        tpl = Path(template)
        env = Environment(
            loader=FileSystemLoader(tpl.parent.as_posix()),
            autoescape=select_autoescape(["html"]),
        )
        self.tpl = env.get_template(tpl.name)

    def render(self, digest: Digest) -> str:
        return self.tpl.render(digest=digest)
