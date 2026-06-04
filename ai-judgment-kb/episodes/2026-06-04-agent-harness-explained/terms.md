# Glossary: Agent Harness

**From:** 十字路口 × 新路 | 2026.06.04

---

| Term | Definition | You'll hear this when... |
|---|---|---|
| **Agent Harness** | 模型以外的一切工程基础设施：工具、上下文管理、记忆、多 agent 编排。通俗理解：模型是大脑，harness 是身体和机甲。 | 讨论 agent 产品架构、选技术栈、评估竞品技术方案 |
| **CLI (Command Line Interface)** | 命令行接口。给 agent 提供 `git`、`ls`、`grep` 等 Unix 命令作为工具。新路的核心论点：CLI 是 agent 的最佳工具接口，因为预训练语料中 Unix 命令占比极高。 | 讨论 agent 工具链设计、MCP vs CLI 辩论 |
| **MCP (Model Context Protocol)** | Anthropic 提出的模型上下文协议，用于标准化 agent 与外部工具的连接方式。新路的观点：MCP 不如 CLI，因为它是新协议，模型训练语料中占比极低。 | 讨论 agent 工具标准、Anthropic 生态、工具链选型 |
| **Prompt Caching** | LLM 推理优化技术：相同前缀的 prompt 可以复用之前计算的 KV cache，大幅降低延迟和成本。新路的关键洞察：随意修改 system prompt 或裁剪历史会破坏 caching。 | 讨论性能优化、成本控制、上下文管理策略 |
| **KV Cache** | Key-Value Cache，Transformer 推理时缓存的注意力计算结果。Prompt caching 依赖 KV cache 复用来加速推理。 | 讨论模型推理、性能优化、API 成本 |
| **上下文卸载 (Context Offloading)** | 当模型上下文窗口满后，将不必要的信息移除、将必要信息压缩或转移到外部存储的策略。新路认为这是 harness 第二层的核心问题。 | 讨论长任务 agent、上下文管理、token 预算 |
| **上下文接力 (Context Handoff)** | 当一个 agent 的上下文窗口满后，创建一个新的 agent 实例，通过"交接文档"传递当前进度和状态，让新 agent 继续完成任务。 | 讨论长任务 agent、多 agent 系统、任务连续性 |
| **Auto-Dream / 记忆整理** | Cloud Code 的记忆后台整理机制：每隔一天，后台 agent 回顾最近对话，提取洞察、纠正错误记忆、合并重复信息。类比人做梦时的记忆巩固。 | 讨论 memory、agent 自我迭代、Cloud Code 设计 |
| **Skills（Agent Skills）** | Agent 的可复用能力模块，类似于 SOP。与 memory 的区别：skills 是可标准化、可传播的；memory 是个性化的经验积累。但两者边界模糊。 | 讨论 agent 能力复用、个人化 vs 标准化 |
| **Agent-Native Model（智能体模型）** | 专为长程任务和多步自主决策训练的模型，区别于传统的问答模型。S PIC 率先转型，OpenAI 从 25 年下半年才开始追赶。 | 讨论模型选型、SOTA 模型能力对比 |
| **Prompt Flow / Node-based Agent** | 基于预设 prompt 节点和状态图的 agent 开发方式（LangChain、LangGraph 为代表）。程序员预先定义每个步骤的输入输出和流转条件。新路认为这套方法论正在被淘汰。 | 讨论 agent 框架选型、LangChain vs agent-native |
| **Unix Computer（虚拟 Unix 计算机）** | 新路的公司 1KB 做的产品：在内存中用数据结构实现一台虚拟 Unix 计算机，给 agent 提供"原生"的工作环境。核心理念：agent 最熟悉 Unix，所以给它 Unix。 | 讨论 agent 运行环境、沙箱方案、1KB/CRAI 产品 |
| **Tension Map（张力地图）** | 当播客没有清晰框架时，将未解决的竞争性观点之间的张力作为输出——"On one hand X, on the other hand Y." | 讨论播客内容提取、知识的结构化方法 |
