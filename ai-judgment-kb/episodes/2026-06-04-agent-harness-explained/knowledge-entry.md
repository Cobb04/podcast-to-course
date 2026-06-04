# Episode Knowledge Entry: Agent Harness 深度拆解

**Episode:** 十字路口 × 新路（CRAI/1KB 创始人）
**Date:** 2026-06-04

---

## Core Thesis

Agent 的上限由 harness 决定 — 模型是大脑，harness（工具、上下文管理、记忆、编排）是身体和机甲。在模型能力趋同的时代，harness 成为产品差异化的真正来源。好的 harness 必须与模型运行原理自洽，且与模型未来进步方向正交。

---

## Reusable Frameworks

- **Harness 三层架构**: 执行能力层（工具）→ 上下文状态层（记忆/skills）→ 编排治理层（多 agent 协调）。用于评估 agent 产品成熟度。
  - **Relationship to existing KB**: NEW — 第一个知识库条目，无现有框架可关联

- **双自洽标准**: 好 harness = 与模型运行原理自洽 + 与模型进步方向正交。用于判断技术方案优劣。
  - **Relationship to existing KB**: NEW

- **More Context, Less Control**: Agent 开发的范式原则 — 给模型充分的工具和上下文，让它自主决策，而非程序员预设每一步。
  - **Relationship to existing KB**: NEW

---

## Key Concepts Introduced

- Agent Harness, CLI vs MCP, Context Offloading, Context Handoff, Auto-Dream, Agent-Native Model, Prompt Caching / KV Cache, Unix Computer, Skills vs Memory 边界
- **Already in KB**: 无 — 第一个条目

---

## Connects To Previous Knowledge

- **Similar to**: 无 — 首个条目
- **Contradicts**: 无 — 首个条目
- **Extends**: 无 — 首个条目

---

## Credibility Summary

- 🟢 High-evidence claims: 0 — 本期无已发表数据或系统性基准测试支撑
- 🟡 Medium-evidence claims: 5 条核心观点 — 均来自新路的直接工程实践 + Cloud Code 源码分析
- 🔴 Low-evidence claims: 3 条 — 未来 2-3 年预测、零人公司愿景、产品经理定义变化的观点

**注意：** 本期嘉宾观点整体 🟡（经验支撑），不是 🟢（数据支撑）。新路有强审美偏好和创业公司立场。他的框架非常有用，但应视为"一个有经验的 builder 的判断"，而非"已被验证的行业共识"。

---

## KB Maintenance Actions

- [x] Create new framework card for [[Harness 三层架构]]
- [x] Create new framework card for [[双自洽标准]]
- [x] Create decision checklist for agent 产品技术选型
- [ ] Future: if a subsequent episode references CLI > MCP with benchmark data, upgrade credibility to 🟢
- [ ] Future: if an episode from a LangChain/Anthropic perspective contradicts the "CLI > MCP" claim, flag as contradiction
