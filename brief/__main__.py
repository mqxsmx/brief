"""入口:python -m brief run <brief-name>"""
from __future__ import annotations
import sys

from .config import load_config, find_brief
from .pipeline import run


def _load_plugins():
    """导入各插件模块,触发 @register_* 注册。

    新增插件后,在此加一行 import 即可被 config 引用。
    """
    import sources.github_trending          # noqa: F401
    import processors.hard_filter           # noqa: F401
    import processors.quality_gate          # noqa: F401
    import processors.anti_inflate          # noqa: F401
    import processors.score_rank            # noqa: F401
    import processors.dedupe                # noqa: F401
    import processors.ai_filter             # noqa: F401
    import renderers.html_renderer          # noqa: F401
    import channels.email_channel           # noqa: F401
    import channels.console_channel         # noqa: F401


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2 or argv[0] != "run":
        print("用法: python -m brief run <brief-name>")
        print("可用简报见 config.yaml")
        return 1

    name = argv[1]
    _load_plugins()
    cfg = load_config()
    brief_cfg = find_brief(cfg, name)
    digest = run(brief_cfg)
    print(f"[brief] 完成: {digest.title} | 入选 {len(digest.projects)} 项 | date={digest.date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
