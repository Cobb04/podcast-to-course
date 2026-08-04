# Podcast to Course

[English](README_EN.md) | [中文](README.md)

**听完播客后，知识像尿一样流走了吗？用我们这个skill，让播客知识化身湿气💩，粘在我们的脑子上。**

一个 Agent 技能——把任何播客转写文件变成**可复用的 AI 产品经理课程**，让洞见不再听完就忘，而是持续沉淀、复利增长，真正改变你做产品决策的方式。

给它一份转写文件，或者直接给一个公开的小宇宙 / 音频链接。它可以先在 Apple Silicon Mac 上免费本地转写，再产出结构化框架卡、决策清单、面试表达素材、个人成长日志——对于里程碑级别的单集，还能生成一个漂亮的交互式 HTML 课程。

## 谁需要这个？

**AI产品实习生/想找到AI产品实习的同学/传统产品想转AI产品/创业者/Builder**——你听了大量 AI/Agent/AI 产品播客，但听完就忘，无法系统化，更无法应用到实际工作中。

你在通勤、健身、做家务时听播客。听到某个洞见时觉得醍醐灌顶——但几天后就忘了。你没有一套系统来捕获、整理、内化你听到的东西。

**你的目标是实用，不是学术：**
- 从对话中提取可复用的思维模型，应用到自己的产品/商业决策中
- 建立产品直觉——知道哪些 AI 模式该跟，哪些该忽略
- 通过内化资深 builder 的 tradeoff 思维，做出更快更好的判断
- 在开会、面试、汇报时有结构化框架脱口而出
- 把不同单集的洞见串联起来——看到第 7 期如何在第 2 期和第 5 期的基础上延伸

你不是要成为研究员。你要的是把播客里的智慧转化成明天早上就能用的工具。

## 三种输出深度模式！

### 模式 1：10 分钟学习卡（超模轻食版）

一个 markdown 文件，10 分钟扫完：核心问题 + 3 个核心判断 + 3 个反直觉洞见 + 1 个可复用框架 + 5 条行动建议 + 1 道自测题。

适合日常听完快速复盘。

### 模式 2：学习笔记 + 框架卡（标准版，默认大碗）

一组可拖入 Notion、Obsidian 的 markdown 资产：
- `EPISODE-HOME.md` — 单集强入口：学习、验证、应用、反驳从这里开始
- `summary.md` — 结构化摘要 + 逻辑地图
- `framework-card.md` — 命名框架 + 决策规则 + 边界条件
- `decision-checklist.md` — 从本期提炼的"何时做什么"清单
- `interview-answer-bank.md` — 面试/汇报用 30 秒/60 秒回答模板
- `claim-ledger.md` — 每条核心 claim 的时间戳、原文锚点、可信度、状态
- `debate-arena.md` — AI 与嘉宾辩论场：质疑高影响观点，必要时 web-search
- `wiki-change-report.md` — 本期对知识库新增、更新、矛盾、开放问题的报告
- `growth-log.md` — 你的 AI 世界观"前后对比"快照
- `knowledge-entry.md` — 跨集连接 + 可信度汇总

适合希望沉淀到个人知识库的深度学习者。

### 模式 3：交互式 HTML 课程（超级碗）

一个零依赖、双击即开的单文件 HTML。面向 Karpathy、OpenAI、产品负责人访谈这种你会反复参考的里程碑级单集。

- **原话 ↔ 可操作洞见对照** — 左边嘉宾原话，右边提炼成可以立刻用的判断
- **框架逐层展开** — 点击按钮一步步展开决策框架的每一层
- **场景判断测验** — 不是"嘉宾说了什么"，而是"你遇到 X 情况，用本期框架怎么判断"
- **对话流动画** — iMessage 风格呈现播客中的观点交锋
- **可信度标签** — 每个观点标注 🟢 数据支撑 / 🟡 经验支撑 / 🔴 推测
- **学习闭环** — pre-test、应用练习、24 小时复习卡，避免只看完不内化
- **知识库持久化** — 每处理一期自动更新总索引，标记与往期的关联

## 三种使用模式

| 模式 | 你给什么 | 你得到什么 |
|---|---|---|
| `/podcast-preview` | 标题 + 嘉宾名 | 值不值得听（1-10 分）+ 3 个带着听的问题 + 可跳过部分 |
| `/podcast-course` | 完整转写文件 | Tier 1/2/3 输出 |
| `/podcast-review` | 你自己的听后感 | 偏差检查 + 遗漏补充 + 框架精炼 |

## 支持的输入格式

WhisperKit 本地转写 · 通义听悟 · 飞书妙记 · YouTube transcript · 小宇宙公开链接 · 公网 `.m4a/.mp3` 链接 · 任意 STT 工具转写 · 你自己的笔记

## 输入模式（自动转写入口）

还没有转写稿？`podcast-to-course/scripts/ingest_podcast.py` 可以帮你生成。默认 `--provider auto`：优先使用免费的本地 WhisperKit，未安装时才回退到已配置的通义听悟。

### 本地免费方案（推荐）

需要 Apple Silicon Mac。WhisperKit 与 SpeakerKit 都通过 [Argmax OSS Swift](https://github.com/argmaxinc/argmax-oss-swift) CLI 调用，音频和转写过程留在本机；首次运行会联网下载模型。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install whisperkit-cli
```

如果 Homebrew 下载失败，也可以从官方 Swift 仓库构建 CLI，并通过
`--whisperkit-cli /path/to/argmax-cli` 指定可执行文件：

```bash
git clone https://github.com/argmaxinc/argmax-oss-swift.git
cd argmax-oss-swift
swift build -c release --product argmax-cli
```

超过 2 小时的音频会使用增量加载和 VAD 切块，不设人为时长上限；实际速度与上限由 Mac 性能、磁盘和模型决定。默认开启 SpeakerKit 说话人分离。
正文始终来自 WhisperKit 原生词级时间戳，RTTM 只负责说话人归属，避免分离结果把 `LibLib`、`PMF` 等词拆坏。系统还会以物理音频时长校验尾部漂移，并输出机器可读的质量指标。

### 三种互斥输入

**1. Transcript Mode — 你已有转写稿（免费、纯本地、不调 API）**

```bash
python podcast-to-course/scripts/ingest_podcast.py \
  --transcript path/to/transcript.md \
  --out outputs/demo
```

**2. Xiaoyuzhou URL Mode — 小宇宙公开单集链接**

```bash
python podcast-to-course/scripts/ingest_podcast.py \
  --url "https://www.xiaoyuzhoufm.com/episode/..." \
  --out outputs/demo
```

先解析页面里的公开 `audio_url`，下载到可续传的本地缓存，再由 WhisperKit 转写并产出 `transcript.md`。

**3. Audio URL Mode — 公网可直接访问的音频文件 URL**

```bash
python podcast-to-course/scripts/ingest_podcast.py \
  --audio-url "https://example.com/audio.m4a" \
  --out outputs/demo
```

常用参数：

```bash
# 明确使用本地 provider；已知是双人访谈可指定人数
python podcast-to-course/scripts/ingest_podcast.py \
  --audio-url "https://example.com/audio.m4a" \
  --provider whisperkit \
  --speaker-count 2 \
  --prompt "LibLib，陈冕，Evoken" \
  --out outputs/demo

# 默认 4 个 VAD worker；内存紧张时可调低
python podcast-to-course/scripts/ingest_podcast.py \
  --audio-url "https://example.com/audio.m4a" \
  --concurrent-worker-count 2 \
  --out outputs/demo

# 网络不稳定时，可预先下载模型并全程使用本地路径
python podcast-to-course/scripts/ingest_podcast.py \
  --audio-url "https://example.com/audio.m4a" \
  --provider whisperkit \
  --whisperkit-cli /path/to/argmax-cli \
  --model-path /path/to/whisperkit-coreml-model \
  --diarization-model-path /path/to/speakerkit-coreml \
  --speaker-count 2 \
  --out outputs/demo

# 关闭说话人分离，减少内存开销
python podcast-to-course/scripts/ingest_podcast.py \
  --audio-url "https://example.com/audio.m4a" \
  --no-diarization \
  --out outputs/demo
```

每次成功会保留可审计的中间产物：

```text
outputs/demo/
├── source_audio.m4a            # 可续传的本地缓存，扩展名按源文件决定
├── source_audio.m4a.download.json # URL、字节数、ETag 等缓存身份
├── whisperkit_native/          # WhisperKit 原生 JSON + SRT + 原始 RTTM
├── whisperkit.log              # 完整命令和 CLI 输出
├── raw_transcription.json      # provider 无关的稳定中间格式
├── transcription_metrics.json # 时长、漂移、词数、覆盖率与质量警告
├── transcript.md               # 课程生成的唯一输入
└── ingest_report.md            # provider、模型、路径和错误记录
```

### 通义听悟回退（可选）

若要显式使用云端听悟，传 `--provider tingwu` 并配置自己的阿里云密钥（绝不提交）：

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="..."
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."
export TINGWU_APP_KEY="..."
```

建议先用官方短音频验证：`python podcast-to-course/scripts/tingwu_smoke_test.py`。

**边界说明。**
- 只支持**公开可访问**内容。不绕过登录、付费、会员、加密、私有内容。
- 本地方案会下载音频到输出目录，并在后续重跑时复用或续传；大文件不会提交到 Git。
- 完整缓存只在 URL 与字节数均匹配时复用；同名但不同来源的音频不会误命中。
- `auto` 的顺序是 WhisperKit → 已配置的听悟。需要固定行为时显式传 `--provider`。
- 通义听悟**仅用于 ASR 转写**——其摘要/章节/问答能力不作为课程内容。
- WhisperKit 与 `--transcript` 不产生 ASR API 费用；只有选中听悟时才可能产生云端费用。
- 自动解析或转写失败时，不能用 shownotes 冒充全文；请检查 `ingest_report.md`，或回退到 Transcript Mode。

## 设计哲学

### 提炼判断力，不做摘要

摘要告诉你"说了什么"。判断提炼告诉你**什么时候用、什么时候不用、该信几分**。每个观点带可信度标签。每个框架有边界条件。"这期很有启发"这种空话被明确禁止——如果一段输出能套在同类话题的任何一期上，那是摘要，不是提炼。

### 考应用，不考记忆

每道测验都把你放在真实场景里。"你的 CTO 提了一个 multi-agent 方案。用本期框架，你的第一反应应该是什么？"——而不是"嘉宾关于 multi-agent 说了什么？"

### 知识复利

每期更新你的个人 AI 判断库。`knowledge-entry.md` 把新洞见和往期连接——标记是强化、矛盾、还是延伸。20 期之后，你有大约 15 张精炼过的框架卡，而不是 60 张重复的。

### 防止播客污染 Wiki

播客发言不是事实源，而是 claim source。高影响观点必须进入 `claim-ledger.md` 和 `debate-arena.md`：先贴出嘉宾原话，再由 AI 质疑逻辑漏洞、样本偏差、因果过度归纳、与已有 wiki 的冲突；遇到产品状态、市场数据、研究结论等可能随时间变化的事实，必须 web-search。

每条核心 claim 都有状态：

```text
accepted / tentative / challenged / disputed / outdated / rejected
```

只有经过锚点、证据、状态和必要质疑的判断，才能进入长期 wiki。

### 诚实校准

AI 播客最危险的是"听起来很对但毫无依据"的判断。每条洞察标注证据来源。嘉宾犹豫的地方，输出保留那种不确定性。遇到没有清晰框架的单集，输出直接说"本期框架密度低"——而不是硬编一个看起来像样子的模型。

### 可移植

Markdown 哪里都能用。HTML 零依赖自包含。不绑定任何平台。你的判断库跟着你的思考走。

## 安装

```bash
git clone https://github.com/Cobb04/podcast-to-course.git ~/.agents/skills/podcast-to-course
```

然后在 Claude Code 里说：*"帮我把这期播客转成课程"*

## 技能文件结构

```
.
├── README.md                        # 中文首页（默认）
├── README_EN.md                     # 英文版说明
├── requirements.txt                 # ingest 层依赖（下载/解析；听悟 SDK 为可选 provider）
├── .env.example                     # 凭据模板（绝不提交真实密钥）
└── podcast-to-course/
    ├── SKILL.md                      # 主技能指令
    ├── scripts/                      # ingest 层 → 产出 transcript.md
    │   ├── ingest_podcast.py         # 统一 CLI（url / audio-url / transcript）
    │   ├── audio_download.py         # 公网音频缓存 + 断点续传
    │   ├── extract_xiaoyuzhou_audio.py
    │   ├── whisperkit_client.py      # 免费本地 WhisperKit/SpeakerKit provider
    │   ├── tingwu_client.py          # 通义听悟离线转写封装
    │   ├── tingwu_smoke_test.py
    │   └── normalize_transcript.py
    └── references/
        ├── build-self-contained.sh   # 通用构建管线
        ├── podcast-engine.js         # 交互引擎（测验、框架展开、导航）
        ├── podcast-styles.css        # 播客专用样式
        ├── debate-arena-template.md  # AI 与嘉宾辩论场模板
        ├── claim-ledger-template.md  # claim 证据账本模板
        ├── episode-home-template.md  # 单集强入口模板
        ├── gotchas.md                # 常见踩坑清单
        └── interactive-elements.md   # 测验、框架、注释等交互模式
```

---

用 Claude Code 构建。基于 [codebase-to-course](https://github.com/zarazhangrui/codebase-to-course) 技能，由 [Zara](https://x.com/zarazhangrui) 原创。
