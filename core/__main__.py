"""入口:python -m core run <brief-name>"""
from __future__ import annotations
import sys

from .config import load_config, find_brief
from .pipeline import run


def _load_plugins():
    """导入各插件模块,触发 @register_* 注册。

    新增插件后,在此加一行 import 即可被 config 引用。
    """
    import sources.github_trending          # noqa: F401
    import sources.hackernews               # noqa: F401
    import sources.arxiv                    # noqa: F401
    import sources.producthunt              # noqa: F401
    import processors.hard_filter           # noqa: F401
    import processors.dedupe                # noqa: F401
    import processors.ai_filter             # noqa: F401
    import renderers.html_renderer          # noqa: F401
    import channels.email_channel           # noqa: F401
    import channels.console_channel         # noqa: F401
    _load_brief_plugins()


def _load_brief_plugins():
    """加载 briefs/<brief>/processors/ 下的专属 processor(只服务某 brief 的过滤逻辑)。

    通用 processor 由上方 import 显式加载;这里扫描各 brief 目录下的专属 processor,
    用路径加载(brief 名可含连字符,无需作 Python 包名)。新增 .py 文件自动加载并注册。
    """
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "briefs"
    if not root.exists():
        return
    for brief_dir in sorted(root.iterdir()):
        proc_dir = brief_dir / "processors"
        if not proc_dir.is_dir():
            continue
        for py in sorted(proc_dir.glob("*.py")):
            if py.name.startswith("_"):
                continue
            spec = importlib.util.spec_from_file_location(
                f"briefs.{brief_dir.name}.processors.{py.stem}", py)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2 or argv[0] != "run":
        print("用法: python -m core run <brief-name>")
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
