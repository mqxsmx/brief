"""插件注册表。

各连接器(Source / Processor / Renderer / Channel)通过装饰器注册,
config.yaml 按名字引用。新增插件 = 写一个类 + 加一行 @register_*。
"""
from __future__ import annotations

SOURCES: dict[str, type] = {}
PROCESSORS: dict[str, type] = {}
RENDERERS: dict[str, type] = {}
CHANNELS: dict[str, type] = {}


def _make(registry: dict[str, type], kind: str):
    def deco(name: str):
        def wrap(cls):
            if name in registry:
                raise ValueError(f"{kind} 已注册: {name}")
            registry[name] = cls
            return cls
        return wrap
    return deco


register_source = _make(SOURCES, "source")
register_processor = _make(PROCESSORS, "processor")
register_renderer = _make(RENDERERS, "renderer")
register_channel = _make(CHANNELS, "channel")
