"""第 5 层(可选):LLM 语义判别 + 中文精读。

TODO: 接 DeepSeek API(或任意 OpenAI 兼容接口):
  对每个项目 name + description + README 前 N 字符:
    1) 判断是否营销 / 搬运 / 水内容,剔除或降权
    2) 生成中文精读,填入 p.summary_cn
当前未实现,直接透传 —— 不影响链路运行。
"""
from __future__ import annotations
from brief.registry import register_processor
from brief.base import Processor


@register_processor("ai_filter")
class AiFilter(Processor):
    def __init__(self, api_base: str | None = None, model: str = "deepseek-chat",
                 api_key_env: str = "DEEPSEEK_API_KEY"):
        self.api_base = api_base
        self.model = model
        self.api_key_env = api_key_env

    def process(self, projects):
        # TODO: 实现 LLM 调用
        return projects
