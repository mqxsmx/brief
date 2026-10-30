"""HTML 渲染器:用 Jinja2 模板把 Digest 转成 HTML 邮件。"""
from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from brief.registry import register_renderer
from brief.base import Renderer
from brief.models import Digest


@register_renderer("html")
class HtmlRenderer(Renderer):
    def __init__(self, template: str = "templates/email.html.j2"):
        tpl = Path(template)
        env = Environment(
            loader=FileSystemLoader(tpl.parent.as_posix()),
            autoescape=select_autoescape(["html"]),
        )
        self.tpl = env.get_template(tpl.name)

    def render(self, digest: Digest) -> str:
        return self.tpl.render(digest=digest)
