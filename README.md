# Brief

> 📬 可扩展的内容聚合 → 精选 → 推送平台

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![LLM](https://img.shields.io/badge/LLM-OpenAI%20Compatible-orange)
![Push](https://img.shields.io/badge/Push-SMTP%20Email-yellow)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)

从多个数据源拉取内容 → 过滤垃圾提取精华 → 渲染成简报 → 推送到多个渠道;每个简报可独立周期(日/周/月)。

首个可用链路:**GitHub Trending(每周)→ 多层过滤 → LLM 中文精读 → 杂志感 HTML 邮件 → SMTP**。

## ✨ 特性

- 🔌 **插件化架构**:四段式 pipeline(Source → Processor → Renderer → Channel),写一个类 + 装饰器即注册,config 加一行即启用
- 🧩 **配置驱动**:每条 brief 独立 schedule/源/处理/渲染/渠道,新增简报零改代码
- 📦 **per-brief 资源独立**:提示词/模板/专属 processor/配置归各 brief 目录,公共默认在 `config.yaml`
- 🤖 **LLM 中文精读**:任意 OpenAI 兼容接口生成简介 + 价值亮点 + 编辑点评,凭据走环境变量,fork 即用
- 🛡️ **反刷榜**:fork-star 比 + 增量占比检测可疑项目,标记降权而非误删
- 🎨 **杂志感邮件**:统一大卡片、深色刊头、金色点缀,每条项目都是头条式呈现
- 🐛 **优雅降级**:缺 SMTP/LLM 凭据自动降级(控制台/英文),永远能跑

## 📐 架构

```
config.yaml(公共 defaults)+ briefs/<brief>/config.yaml(各 brief 独立配置,继承 defaults)
        │  python -m core run <brief-name>
        ▼
Source(可多源聚合) → Processor 链(过滤/去重/打分/可选AI) → Renderer → Channel(可多渠道)
```

四层插件各司其职:`Source` 取数据 / `Processor` 过滤打分 / `Renderer` 渲染 / `Channel` 推送。引擎(`core/`)只提供「契约 + 注册 + 编排 + 入口」,业务全在插件。

## 📁 目录结构

```
brief/
├── .github/workflows/        # GitHub Actions:reusable + 每 brief 一个 caller
├── core/                     # 引擎(base/models/registry/config/pipeline/__main__)
├── sources/                  # 通用数据源连接器
├── processors/               # 通用 processor(hard_filter/dedupe/ai_filter)
├── renderers/                # 通用渲染器(html)
├── channels/                 # 通用投递渠道(email/console)
├── briefs/                   # per-brief 专属资源(配置/提示词/模板/专属processor)
│   └── github-trending-weekly/
│       ├── config.yaml       # 本 brief 配置(继承 config.yaml 的 defaults)
│       ├── prompt.md         # LLM 提示词
│       ├── template.html.j2  # 专属邮件模板
│       └── processors/       # 本 brief 专属(quality_gate/anti_inflate/score_rank)
├── config.yaml               # 公共配置(defaults:默认 renderer/channels)
└── requirements.txt
```

| 目录 | 职责 | 复用范围 |
|------|------|---------|
| `core/` | 引擎(契约/注册/编排/入口) | 全局 |
| `sources/` `processors/` `renderers/` `channels/` | 通用插件 | 跨 brief 复用 |
| `briefs/<brief>/` | per-brief 资源(配置/提示词/模板/专属processor) | 只服务该 brief |

## 🚀 快速开始(本地 dry-run)

无需配置邮箱即可跑,邮件内容会**打印到控制台**:

```bash
pip install -r requirements.txt
python -m core run github-trending-weekly
```

`quality_gate` 会调 GitHub API。匿名调用限额 60 次/小时,建议设置 token 提到 5000 次/小时:

```powershell
# PowerShell
$env:GITHUB_TOKEN = "你的 GitHub PAT"
python -m core run github-trending-weekly
```

## 🔧 配置 QQ 邮箱

1. QQ 邮箱 → 设置 → 账户 → 开启 **SMTP 服务**,获取**授权码**(不是登录密码)。
2. 设置环境变量:

```powershell
$env:SMTP_HOST     = "smtp.qq.com"
$env:SMTP_PORT     = "465"
$env:EMAIL_ADDRESS = "你的@qq.com"
$env:EMAIL_PASSWORD = "授权码"
$env:EMAIL_TO      = "收件邮箱@example.com"
```

3. 再次运行即发真实邮件:`python -m core run github-trending-weekly`

## 🤖 LLM 配置(中文精读,可选)

`ai_filter` 用任意 **OpenAI 兼容接口**生成中文简介 + 价值亮点 + 编辑点评。**未配置则降级为英文简介,不影响发送。**

LLM 配置**全部从环境变量读**(不写进 config),便于 GitHub Actions 用 Secrets 配置,fork 后无需改代码:

| 环境变量 | 说明 | 示例(DeepSeek) |
|----------|------|------------------|
| `LLM_API_BASE` | 接口地址 | `https://api.deepseek.com` |
| `LLM_MODEL` | 模型名 | `deepseek-flash` |
| `LLM_API_KEY` | API key | `sk-...` |

**换厂商**只需改这三个环境变量(无需单独配「厂商」,`api_base` + `model` 已唯一确定):

| 厂商 | LLM_API_BASE | LLM_MODEL | 获取 key |
|------|--------------|-----------|---------|
| DeepSeek(推荐,便宜中文好) | `https://api.deepseek.com` | `deepseek-flash` | platform.deepseek.com |
| OpenAI | `https://api.openai.com` | `gpt-4o-mini` | platform.openai.com |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode` | `qwen-plus` | dashscope.aliyuncs.com |
| 智谱 | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | open.bigmodel.cn |
| Ollama(本地,无需 key) | `http://localhost:11434/v1` | `llama3` | 本地运行 |

本地测试:

```powershell
$env:LLM_API_BASE = "https://api.deepseek.com"
$env:LLM_MODEL    = "deepseek-flash"
$env:LLM_API_KEY  = "sk-..."
python -m core run github-trending-weekly
```

**提示词可定制**:每个 brief 的提示词在 `briefs/<brief>/prompt.md`,改这个文件即可调整解读风格/侧重(如技术选型/趋势解读/生态适用),不用改代码。brief config 里 `ai_filter` 的 `prompt_file` 指向它,`{items}` 处自动填入项目数据。

## 🚢 部署到 GitHub Actions(public 仓库)

1. 将本项目推送到 GitHub **public** 仓库(Actions 完全免费)。
2. 仓库 **Settings → Secrets and variables → Actions** 添加:

   | Secret | 值 |
   |--------|----|
   | `SMTP_HOST` | `smtp.qq.com` |
   | `SMTP_PORT` | `465` |
   | `EMAIL_ADDRESS` | 你的 QQ 邮箱 |
   | `EMAIL_PASSWORD` | 授权码 |
   | `EMAIL_TO` | 收件邮箱 |
   | `LLM_API_BASE` | LLM 接口地址(可选,不配则简介为英文) |
   | `LLM_MODEL` | LLM 模型名(可选) |
   | `LLM_API_KEY` | LLM key(可选) |

   > `GITHUB_TOKEN` 由 Actions 自动提供,无需手动配置。

3. 进入 **Actions** 页面 → 选 `brief-github-weekly` → `Run workflow` 手动测试一次。
4. 之后每周一北京时间约 08:00 自动发送。

### ⏰ cron 时区速查(GitHub 用 UTC,北京 +8)

| 触发时间(北京) | cron |
|------------------|------|
| 每天 08:00 | `0 0 * * *` |
| 每周一 08:00 | `0 0 * * 1` |
| 每月 1 号 08:00 | `0 0 1 * *` |

新增日/月简报:复制一个 caller workflow,改 `cron` 和 `brief` 名即可。

## 🔍 过滤链(以 github-trending-weekly 为例)

```
GitHub Trending(~25项)
   ├─ hard_filter      空描述 + 关键词黑名单 → 剔除        [通用]
   ├─ quality_gate     GitHub API 卡阈值 → 剔除 + 存 readme  [本 brief 专属]
   ├─ anti_inflate     fork-star 比 + 增量 → 标记降权       [本 brief 专属]
   ├─ dedupe           去重                          [通用]
   ├─ score_rank       综合评分取 Top 15              [本 brief 专属]
   └─ ai_filter        LLM 中文精读(失败降级英文)    [通用]
   ▼
渲染杂志感 HTML → 发邮件
```

原则:**宁可漏不可错**。硬过滤保守删,模糊判断走评分降权,可疑项在 `extra` 记原因(邮件可见),便于调参。

> 通用 processor(`hard_filter`/`dedupe`/`ai_filter`)放 `processors/`,跨 brief 复用;GitHub 指标专属(`quality_gate`/`anti_inflate`/`score_rank`)放 `briefs/<brief>/processors/`。

## 🧩 扩展指南

| 想加 | 做法 |
|------|------|
| 新数据源 | `sources/xxx.py` + `@register_source` + `__main__.py` 加 import + brief config 加一行 |
| 新通用处理器 | `processors/xxx.py` + `@register_processor` + `__main__.py` 加 import + brief config 加一行 |
| 新专属处理器 | `briefs/<brief>/processors/xxx.py` + `@register_processor`(自动加载)+ brief config 加一行 |
| 新渠道 | `channels/xxx.py` + `@register_channel` + `__main__.py` 加 import + config 加一行 |
| 新简报 | `briefs/<新名>/` 建 `config.yaml`(+ prompt.md / template.html.j2)+ 一个 caller workflow |
| 改邮件样式 | 改 `briefs/<brief>/template.html.j2`(per-brief) |
| 改 LLM 解读风格 | 改 `briefs/<brief>/prompt.md` |
| 改公共默认 | 改 `config.yaml` 的 `defaults` |

## ⚠️ 注意事项

- GitHub Actions `schedule` **不保证准时**,高峰期可能延迟,但一定执行。
- 仓库 **60 天无活动** schedule 会自动暂停,需偶尔提交或手动启用。
- GitHub Trending 页面改版时,`sources/github_trending.py` 的选择器需更新(已用注释标明定位)。

## 🗺️ 路线图

- [ ] 反刷榜 star-history 曲线检测(`briefs/.../processors/anti_inflate.py`)
- [ ] 跨天去重持久化(通用 `processors/dedupe.py`,state.json 或 cache)
- [ ] 新闻 / 视频数据源(`sources/hackernews.py` 等)
- [ ] Telegram / Webhook 渠道(`channels/telegram.py` 等)
- [ ] 日报 / 月报简报

## 📄 License

MIT
