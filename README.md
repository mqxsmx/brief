# Brief

> 可扩展的内容聚合精选推送平台。

从多个数据源拉取内容 → 过滤垃圾提取精华 → 渲染成简报 → 推送到多个渠道;每个简报可独立周期(日/周/月)。

首个可用链路:**GitHub Trending(每日)→ 过滤链 → HTML 邮件 → SMTP**。

## 架构

四段式 pipeline + 插件注册表 + 配置驱动 + 多简报编排:

```
config.yaml(briefs 清单,每条 brief 独立 schedule/源/处理/渲染/渠道)
        │  python -m brief run <brief-name>
        ▼
Source(可多源聚合) → Processor 链(过滤/去重/打分/可选AI) → Renderer → Channel(可多渠道)
```

设计原则:**新增源 / 处理器 / 渲染器 / 渠道 = 写一个类 + config 加一行,主干零改动。**

## 目录结构

```
brief/
├── .github/workflows/        # GitHub Actions:reusable + 每 brief 一个 caller
├── brief/                    # Python 包(models/registry/base/config/pipeline/__main__)
├── sources/                  # 数据源连接器
├── processors/               # 过滤/去重/打分处理器
├── renderers/                # 渲染器
├── channels/                 # 投递渠道
├── templates/email.html.j2   # 邮件模板
├── config.yaml               # 简报清单
└── requirements.txt
```

## 快速开始(本地 dry-run)

无需配置邮箱即可跑,邮件内容会**打印到控制台**:

```bash
pip install -r requirements.txt
python -m brief run github-trending-daily
```

`quality_gate` 会调 GitHub API。匿名调用限额 60 次/小时,建议设置 token 提到 5000 次/小时:

```powershell
# PowerShell
$env:GITHUB_TOKEN = "你的 GitHub PAT"
python -m brief run github-trending-daily
```

## 配置 QQ 邮箱

1. QQ 邮箱 → 设置 → 账户 → 开启 **SMTP 服务**,获取**授权码**(不是登录密码)。
2. 设置环境变量:

```powershell
$env:SMTP_HOST     = "smtp.qq.com"
$env:SMTP_PORT     = "465"
$env:EMAIL_ADDRESS = "你的@qq.com"
$env:EMAIL_PASSWORD = "授权码"
$env:EMAIL_TO      = "收件邮箱@example.com"
```

3. 再次运行即发真实邮件:`python -m brief run github-trending-daily`

## 部署到 GitHub Actions(public 仓库)

1. 将本项目推送到 GitHub **public** 仓库(Actions 完全免费)。
2. 仓库 **Settings → Secrets and variables → Actions** 添加:

   | Secret | 值 |
   |--------|----|
   | `SMTP_HOST` | `smtp.qq.com` |
   | `SMTP_PORT` | `465` |
   | `EMAIL_ADDRESS` | 你的 QQ 邮箱 |
   | `EMAIL_PASSWORD` | 授权码 |
   | `EMAIL_TO` | 收件邮箱 |

   > `GITHUB_TOKEN` 由 Actions 自动提供,无需手动配置。

3. 进入 **Actions** 页面 → 选 `brief-github-daily` → `Run workflow` 手动测试一次。
4. 之后每天北京时间约 08:00 自动发送。

### cron 时区速查(GitHub 用 UTC,北京 +8)

| 触发时间(北京) | cron |
|------------------|------|
| 每天 08:00 | `0 0 * * *` |
| 每周一 08:00 | `0 0 * * 1` |
| 每月 1 号 08:00 | `0 0 1 * *` |

新增周/月简报:复制一个 caller workflow,改 `cron` 和 `brief` 名即可。

## 过滤链(处理垃圾项目)

| 层 | 处理器 | 作用 |
|----|--------|------|
| 1 | `hard_filter` | 空描述 + 关键词黑名单(awesome/面试/template…) |
| 2 | `quality_gate` | 调 GitHub API 卡 forks/watchers/readme/license/年龄/活跃度 |
| 3 | `anti_inflate` | 反刷榜:fork-star 比 + 当日增量占比(标记可疑降权) |
| 4 | `score_rank` | 综合评分取 Top N |
| 6 | `dedupe` | 去重 |

原则:**宁可漏不可错**。硬过滤保守删,模糊判断走评分降权,可疑项在 `extra` 记原因(邮件可见),便于调参。

## 扩展指南

| 想加 | 做法 |
|------|------|
| 新数据源 | 新建 `sources/xxx.py`,用 `@register_source("xxx")` 装饰;在 `__main__.py` 加 import;config 加一行 |
| 新处理器 | 新建 `processors/xxx.py`,`@register_processor("xxx")`;加 import;config 的 processors 加一行 |
| 新渠道 | 新建 `channels/xxx.py`,`@register_channel("xxx")`;加 import;config 加一行 |
| 新简报 | config.yaml 的 `briefs` 加一段(自带 schedule + 链路)+ 一个 caller workflow |
| 改邮件样式 | 改 `templates/email.html.j2` |

## 注意事项

- GitHub Actions `schedule` **不保证准时**,高峰期可能延迟,但一定执行。
- 仓库 **60 天无活动** schedule 会自动暂停,需偶尔提交或手动启用。
- GitHub Trending 页面改版时,`sources/github_trending.py` 的选择器需更新(已用注释标明定位)。

## 路线图(已留扩展点,标 TODO)

- 反刷榜 star-history 曲线检测(`processors/anti_inflate.py`)
- 跨天去重持久化(`processors/dedupe.py`,state.json 或 cache)
- AI 中文精读(`processors/ai_filter.py`,接 DeepSeek API)
- 新闻 / 视频数据源、Telegram / Webhook 渠道
- 周报 / 月报简报
