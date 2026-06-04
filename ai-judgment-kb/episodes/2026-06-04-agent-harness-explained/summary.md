# Episode Summary: Agent Harness — 模型以外的工程竞争力

**Episode:** 十字路口 × 新路（CRAI/1KB 创始人）
**Date:** 2026-06-04
**Learning Goal:** AI 产品判断力

---

## Core Question

当模型能力趋同时，**agent harness（模型之外的一切工程实践）** 如何成为产品差异化的真正来源？以及作为 AI PM，如何判断一个 harness 设计是好是坏？

---

## Core Arguments with Credibility

### Argument 1: 模型才是 agent，其他都是 harness
🟡 Medium | 新路的工程实践 + Cloud Code 源码分析

"Agent 从始到终都是一个模型。" 模型是大脑，harness 是身体/机甲。模型决定智力上限（智商 120-170），harness 决定这个智力能发挥多少。重要性排序：模型 > 上下文 > 工具。

**产品含义：** 如果你的 agent 表现不好，第一反应应该是换更强的模型，而非调试 harness。选模型是第一决策，harness 是放大器。

### Argument 2: 好 harness 的双自洽标准
🟡 Medium | 新路的工程实践总结

好 harness 必须：(1) 与模型运行原理自洽（模型是自回归的，应自主决策下一步）；(2) 与模型未来进步方向正交（模型越强，harness 应越强，而非成为瓶颈）。

**产品含义：** 选工具链时问"它会不会因为模型变强而被淘汰？" LangChain 的 prompt flow 模式（预设每一步决策）违反双自洽 → 模型越强越会成为限制。

### Argument 3: CLI > MCP — Unix 哲学是 agent 的原生接口
🟡 Medium | 新路的实际测试 + 预训练语料推理

GitHub CLI 的任务成功率显著高于 GitHub MCP。原因：Unix 命令在预训练语料中出现几十亿次，MCP 是近两年才提出的新协议，语料占比不到 0.1%。"也许我们今天不应该再造更多的轮子，我们就回到 Unix 自洽的哲学中。"

**产品含义：** 给 agent 配工具时优先 CLI/Unix 兼容接口，不要追新协议。

### Argument 4: "More Context, Less Control" — agent 开发的范式转移
🟡 Medium | Cloud Code 源码分析 + 新路的工程实践

Cloud Code 的哲学：给模型充分的工具和上下文，让它自主决策。"Zero control — 最多就是限制你调工具的时候有些工具不能调。" 与传统 prompt flow（程序员预设每一步决策）形成鲜明对比。

**产品含义：** 代理式架构（agent-driven）vs 预设式架构（prompt-flow）是当前 agent 开发的派系之争。前者面向未来，后者面向过去。

### Argument 5: 当下产品经理的定义已经变了
🔴 Low | 新路的个人观点

"今天的产品经理跟过去的产品经理指的不是同一种产品经理。今天是在技术变化周期内，我们所做的一切产品都是在吃这个技术周期变化的红利。" PM 必须同时懂技术变化的本质和场景需求。

---

## Logic Map

```
模型的智能水平（大脑）
        ↓ 决定上限
Harness 工程实践（身体/机甲）
        ↓ 拆分为三层
┌───────┼───────┐
执行层    上下文层   编排层
(工具)   (记忆/状态) (多Agent协调)
        ↓ 设计哲学
"More Context, Less Control"
        ↓ 判断标准
双自洽：与模型原理自洽 + 与模型进步正交
        ↓ 工具选择
CLI > MCP（Unix哲学 > 新协议）
        ↓ 产品启示
选模型第一，harness 放大，框架面向未来
```

---

## Counter-Intuitive Insights

1. **"最好的上下文管理是不做管理。"** 随意裁剪上下文 → 破坏 prompt caching → KV cache 重新计算。你以为在省钱，其实在浪费。

2. **MCP 不如 CLI 不是因为设计问题，是训练语料问题。** 模型见过几十亿条 `git commit`、`ls -la`、`grep`，但几乎没见过 MCP 的协议格式。工具接口的"熟悉度"直接影响任务成功率。

3. **"产品经理画好 UX/UI"的时代过去了。** 现在 PM 的核心能力是理解技术周期变化的内核，把技术进步红利翻译成场景应用。

4. **记忆不应该是知识图谱。** 最好的记忆方案是 Unix files + markdown + agent 维护 — 人容易懂，LLM 也容易懂。半规则式优于全规则式。

5. **大多数 agent 只需要配好 3 类工具就能覆盖 95% 任务：** 文件系统（增删读写搜索）、浏览器（browser）、语言解释器（python/node）。不需要过度设计工具链。

---

## Speaker Mental Model

新路的思考框架是**"从模型视角出发"**的工程哲学：

- 他不是从"开发者怎么方便"出发，而是从"模型怎么工作"出发
- 核心信念：transformers 是自回归的 → 应该让模型自主决策下一步 → 工程应该提供能力而非约束
- 判断框架：任何工程决策都用"双自洽标准"检验 — 符合模型原理吗？不会被模型进步淘汰吗？
- 审美偏好：简洁 > 复杂，Unix > 新协议，数据结构 > 容器，语言层 > 系统层

**注意：** 新路的观点带有强审美偏好和创业公司立场（1KB 在做 Unix computer 方案）。他的判断应标为 🟡（经验支撑），不是 🟢（数据支撑）。
