# Podcast to Course

[English](README_CN.md) | [中文](README.md)

**听完播客后，知识像尿一样流走了吗？用我们这个skill，让播客知识化身湿气💩，粘在我们的脑子上。**

一个 Agent 技能——把任何播客转写文件变成**可复用的 AI 产品经理课程**，让洞见不再听完就忘，而是持续沉淀、复利增长，真正改变你做产品决策的方式。

给它一份转写文件（通义听悟免费10h 我靠求打钱），它产出结构化框架卡、决策清单、面试表达素材、个人成长日志——对于里程碑级别的单集，还能生成一个漂亮的交互式 HTML 课程。

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

通义听悟 · 飞书妙记 · YouTube transcript · 小宇宙 / Apple Podcasts 手动转写 · 任意 STT 工具转写 · 你自己的笔记

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
podcast-to-course/
├── SKILL.md                          # 主技能指令
├── README.md
├── README_CN.md                      # 中文版说明
└── references/
    ├── build-self-contained.sh       # 通用构建管线
    ├── podcast-engine.js             # 交互引擎（测验、框架展开、导航）
    ├── podcast-styles.css            # 播客专用样式
    ├── debate-arena-template.md      # AI 与嘉宾辩论场模板
    ├── claim-ledger-template.md       # claim 证据账本模板
    ├── episode-home-template.md       # 单集强入口模板
    ├── gotchas.md                    # 常见踩坑清单
    └── interactive-elements.md       # 测验、框架、注释等交互模式
```

---

用 Claude Code 构建。基于 [codebase-to-course](https://github.com/zarazhangrui/codebase-to-course) 技能，由 [Zara](https://x.com/zarazhangrui) 原创。
