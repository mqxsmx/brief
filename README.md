# Brief

> 📬 可扩展的内容聚合 → 精选 → 推送平台

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![LLM](https://img.shields.io/badge/LLM-OpenAI%20Compatible-orange)
![Push](https://img.shields.io/badge/Push-SMTP%20Email-yellow)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)

> 🚀 **零服务器、零运维**:全部跑在 GitHub Actions 上 —— fork 本仓库 → 配好邮箱和模型的 Secrets → 每天定时自动发邮件到你邮箱。**不用买服务器、不用长期挂机、不用部署 cron**,public 仓库 Actions 完全免费。

> 🍴 **fork 即用**:改改 `briefs/<brief>/` 下的配置 / 提示词 / 模板,就是你自己专属的每日简报;LLM 凭据走环境变量,fork 后无需改代码。

从多个数据源拉取内容 → 过滤垃圾提取精华 → LLM 中文精读 → 渲染成简报 → 定时推送到邮箱;每个简报可独立周期(日/周/月),GitHub Actions 托管,零服务器。

已有链路:

- **GitHub Trending 周报**:每周一发,Trending 周榜 → 多层过滤(反刷榜)→ LLM 中文精读 → 杂志感邮件
- **Hacker News 日报**:每天发,HN 热门 → points 评分取 Top 20 → LLM 中文解读 + 类别标签 → 按类别分组邮件
- **arXiv AI 论文日报**:每天发,cs.AI/LG/CL 最新论文 → LLM 中文解读摘要 + 打类别 → 按类别分组邮件(学术蓝)
- **Product Hunt 新品日报**:每天发,PH 新品 → LLM 中文解读产品 + 打类别 → 按类别分组邮件(PH 红)

## ✨ 特性

- 🔌 **插件化架构**:四段式 pipeline(Source → Processor → Renderer → Channel),写一个类 + 装饰器即注册,config 加一行即启用
- 🧩 **配置驱动**:每条 brief 独立 schedule/源/处理/渲染/渠道,新增简报零改代码
- 📦 **per-brief 资源独立**:提示词/模板/专属 processor/配置归各 brief 目录,公共默认在 `config.yaml`
- 🤖 **LLM 中文精读**:任意 OpenAI 兼容接口生成简介 + 价值亮点 + 编辑点评,凭据走环境变量,fork 即用
- 🛡️ **反刷榜**:fork-star 比 + 增量占比检测可疑项目,标记降权而非误删
- 🎨 **杂志感邮件**:统一大卡片、深色刊头、金色点缀,每条项目都是头条式呈现
- 🗂️ **多源 + 类别分组**:GitHub 周报(杂志风)、HN 日报(橙)、arXiv 论文日报(学术蓝)、Product Hunt 新品日报(红);LLM 自动打类别标签按类别分组
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
│   ├── github-trending-weekly/
│   │   ├── config.yaml       # 本 brief 配置(继承 config.yaml 的 defaults)
│   │   ├── prompt.md         # LLM 提示词
│   │   ├── template.html.j2  # 专属邮件模板
│   │   └── processors/       # 本 brief 专属(quality_gate/anti_inflate/score_rank)
│   ├── hackernews-daily/
│   │   ├── config.yaml       # HN 日报配置
│   │   ├── prompt.md         # LLM 提示词(中文解读 + 类别标签)
│   │   ├── template.html.j2  # 按类别分组邮件模板(HN 橙)
│   │   └── processors/       # 本 brief 专属(hn_score)
│   ├── arxiv-daily/
│   │   ├── config.yaml       # arXiv 论文日报配置
│   │   ├── prompt.md         # LLM 提示词(解读摘要 + 类别)
│   │   └── template.html.j2  # 按类别分组邮件模板(学术蓝)
│   └── producthunt-daily/
│       ├── config.yaml       # Product Hunt 新品日报配置
│       ├── prompt.md         # LLM 提示词(解读产品 + 类别)
│       └── template.html.j2  # 按类别分组邮件模板(PH 红)
├── config.yaml               # 公共配置(defaults:默认 renderer/channels)
└── requirements.txt
```

| 目录 | 职责 | 复用范围 |
|------|------|---------|
| `core/` | 引擎(契约/注册/编排/入口) | 全局 |
| `sources/` `processors/` `renderers/` `channels/` | 通用插件 | 跨 brief 复用 |
| `briefs/<brief>/` | per-brief 资源(配置/提示词/模板/专属processor) | 只服务该 brief |

## 🚀 快速开始(fork 即用,推荐)

3 步上手,全程在 GitHub 上完成,**无需本地环境、无需服务器**:

**1. fork 本仓库**到你自己的 GitHub 账号(public 仓库 Actions 免费)。

**2. 配置 Secrets**:仓库 **Settings → Secrets and variables → Actions** 添加:

   | Secret | 值 | 必填 |
   |--------|----|------|
   | `SMTP_HOST` | `smtp.qq.com` | ✅ |
   | `SMTP_PORT` | `465` | ✅ |
   | `EMAIL_ADDRESS` | 你的 QQ 邮箱 | ✅ |
   | `EMAIL_PASSWORD` | 邮箱授权码(非登录密码) | ✅ |
   | `EMAIL_TO` | 收件邮箱 | ✅ |
   | `LLM_API_BASE` | LLM 接口地址(如 `https://api.deepseek.com`) | 可选(不配则简介为英文) |
   | `LLM_MODEL` | LLM 模型名(如 `deepseek-flash`) | 可选 |
   | `LLM_API_KEY` | LLM key | 可选 |

   > `GITHUB_TOKEN` 由 Actions 自动提供,无需手动配置。GitHub Trending 周报的 `quality_gate` 会用它调 GitHub API(已自动提额到 5000 次/小时)。

**3. 手动触发一次测试**:进入 **Actions** 页面 → 选对应 caller(`brief-github-weekly` 周报 / `brief-hn-daily` / `brief-arxiv-daily` / `brief-producthunt-daily` 日报)→ `Run workflow`。几分钟后邮件到邮箱 ✅

之后按各自 cron 自动发(见下「发送时间表」)。想改发送时间 / 内容 / 样式,直接改 `briefs/<brief>/` 下的文件,提交即生效。

### 🖥️ 本地运行(可选,开发/调试用)

想本地先跑一遍看效果(邮件内容打印到控制台,不配 SMTP 不发真邮件):

```bash
pip install -r requirements.txt
python -m core run hackernews-daily          # HN 日报(无需 token)
python -m core run arxiv-daily               # arXiv 论文日报(无需 token)
python -m core run producthunt-daily         # Product Hunt 新品日报(无需 token)
python -m core run github-trending-weekly    # GitHub 周报(建议设 GITHUB_TOKEN 提额)
```

邮箱 / LLM 配置本地用环境变量(与上面 Secrets 同名),见下两节;配齐即发真邮件。

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

## ⏰ 发送时间表 & cron 速查

四个 brief 已错开,邮件不会扎堆(cron 在 caller workflow + 各 brief config):

| Brief | 北京时间 | cron |
|-------|---------|------|
| Hacker News 日报 | 每天 08:00 | `0 0 * * *` |
| arXiv 论文日报 | 每天 09:00 | `0 1 * * *` |
| Product Hunt 新品日报 | 每天 10:00 | `0 2 * * *` |
| GitHub Trending 周报 | 每周一 08:00 | `0 0 * * 1` |

GitHub Actions `schedule` 用 UTC(北京 +8),常用时段速查:

| 触发时间(北京) | cron |
|------------------|------|
| 每天 08:00 | `0 0 * * *` |
| 每周一 08:00 | `0 0 * * 1` |
| 每月 1 号 08:00 | `0 0 1 * *` |

新增/改时段简报:复制一个 caller workflow(`.github/workflows/brief-xxx-daily.yml`),改 `cron` 和 `brief` 名即可。

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

### HN 日报过滤链

```
Hacker News front_page(近 24h,points>50)
   ├─ dedupe      去重                          [通用]
   ├─ hn_score    points+comments 评分取 Top 20  [本 brief 专属]
   └─ ai_filter   LLM 中文解读 + 打类别标签       [通用]
   ▼
按类别分组渲染(HN 橙)→ 发邮件
```

类别由 LLM 从「技术 / AI / 创业 / 安全 / 开源 / 科学 / 讨论」中选;无外链的 Ask/Show HN 跳 HN 讨论页。

### arXiv / Product Hunt 日报过滤链

```
arXiv(cs.AI/LG/CL 最新 20 篇) / Product Hunt(近 24h 新品 20 款)
   ├─ dedupe      去重                          [通用]
   └─ ai_filter   LLM 中文解读 + 打类别标签       [通用]
   ▼
按类别分组渲染(学术蓝 / PH 红)→ 发邮件
```

arXiv 类别:LLM / Agent / 视觉CV / 语言NLP / 强化学习 / 多模态 / 系统infra / 理论;PH 类别:AI 应用 / 开发者工具 / 生产力 / 设计创意 / 创业SaaS / 硬件设备。两者源 API 均免费无 token(arXiv Atom API、PH Atom feed)。

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
- [x] Hacker News 日报数据源(`sources/hackernews.py`)+ 类别分组邮件
- [x] arXiv 论文日报(`sources/arxiv.py`)+ Product Hunt 新品(`sources/producthunt.py`)
- [ ] Telegram / Webhook 渠道(`channels/telegram.py` 等)
- [ ] 月报简报

## 📄 License

MIT
