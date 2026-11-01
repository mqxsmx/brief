"""hackernews-daily 的专属 processor 目录。

放只服务本 brief、无法复用的过滤逻辑。新增 .py 文件会被 __main__ 自动加载并注册
(用 @register_processor 装饰)。通用 processor 仍放 processors/。
"""
