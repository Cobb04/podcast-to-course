# Personal AI Growth Log: Agent Harness 深度拆解

**Episode:** 十字路口 × 新路 | 2026.06.04
**Learning Goal:** AI 产品判断力

---

## What I used to think

Agent 产品做得好不好，主要看选了哪个模型 + prompt 写得好不好。Harness 是"工程实现细节"——选个 LangChain 或 LlamaIndex 之类的框架就解决了。工具的接口协议（MCP vs CLI）是工程偏好问题，跟产品关系不大。产品经理不需要理解 harness 的细节，只需要理解用户场景。

---

## What I now think

模型选对了只是起点。真正让一个 agent 产品从"能跑"变成"好用"的是 harness——尤其是上下文管理（第二层）和工具链设计（第一层）。产品经理不需要自己写 harness，但**必须能用"双自洽标准"判断技术方案的好坏**。具体来说：

1. 技术方案是否给模型更多自由（more context, less control）？如果是预设流程式的（prompt flow），它会被模型进步淘汰。
2. 工具接口选 CLI 还是 MCP 不是工程偏好——是训练语料分布决定的成功率差异，直接影响产品体验。
3. 产品差异化不在模型层（大家用的都一样），在 harness 层。

---

## What changed

新路的"harness 三层架构"让我有了一套结构化的评估框架。以前我看一个 agent 产品只会模糊地感觉"好像不够好"，现在我能定位到具体是哪一层没做好——是工具没配够（第一层），记忆跨 session 就丢（第二层），还是多 agent 协调混乱（第三层）。

另外，新路的"双自洽标准"是一个我立刻能用的面试/评审工具——我不需要懂代码，只需要问"这个设计是给模型更多自由还是更多约束？"就能判断技术方案的方向对不对。

---

## Next time I encounter an agent 产品技术评审, I will ask:

1. **这个设计是"more context, less control"还是反过来？** 如果工程团队预设了很多流转规则和条件路由，挑战它。
2. **这个框架会随着模型变强而变强，还是会被淘汰？** 如果框架需要"限制模型能力"来工作，它活不过下一代模型。
3. **产品卡在 harness 三层中的哪一层？** 第一层是 demo，第二层是产品，第三层是平台。我们现在的产品阶段和目标匹配吗？

---

## I want to test this by

在接下来的 2 周内，用"harness 三层架构"分析 3 个我常用的 agent 产品（比如 Cursor、Claude Code、Perplexity），判断它们分别做到了哪一层，差异在哪。然后输出一份"竞品 harness 成熟度对比"给自己看。
