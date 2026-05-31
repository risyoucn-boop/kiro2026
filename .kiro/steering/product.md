---
inclusion: always
---

# Synapse Nexus — 项目背景与工作约定

## 这是什么

**Synapse Nexus**（中文名"言枢"待定）是一款中英文混说语音输入法。

- 主要平台：**Ubuntu（v1.0）→ Windows（v1.1）→ iOS（v1.2）→ macOS（v2.0）**
- 单一开发者 + AI 协同工作流
- 商业模式：**按量付费**（明确反订阅制）

权威文档（按重要性）：
1. `docs/PRD.md` — 做什么 / 为什么 / 成功标准
2. `docs/ARCHITECTURE.md` — 怎么做（技术）
3. `docs/ROADMAP.md` — 8 周路线图 + 之后

## 核心架构口径（修改前请确认）

- **Core 是 Rust**，平台前端只做 UI / 音频采集 / 文本注入
- **Provider 抽象**：ASR、Polish、计费 全部 trait 化，不准把 doubao / qwen 这些名字泄漏到 core 业务逻辑
- **Polish 是 best-effort**：≤ 600ms 必须返回，否则回退原始 ASR
- **Polish 必须做差异审计**（edit_ratio > 30% 或新增命名实体直接拒绝）
- **跨平台 75% 代码复用**是项目能成立的前提，违反此原则的 PR 需要正当理由

## 不可妥协的产品决策

- ❌ **不做订阅制**（按量付费 + 阶梯定价）
- ❌ **不持久化任何音频**（识别完即丢）
- ❌ **不用用户数据训练**
- ❌ **不做方言 / 不做离线纯本地（兜底除外）/ 不做拼音五笔**
- ✅ **延迟 > 精度**（首字 P95 ≤ 1.5s 是生死线）
- ✅ **失败永远有路可走**（云端 ASR 挂 → 本地兜底；Polish 挂 → 原始 ASR）

## 编码与协作

- Rust：edition 2021，`cargo fmt` + `clippy -- -D warnings` 必过
- C++（fcitx5 engine）：C++17，clang-format
- 提交信息：Conventional Commits（`feat:` / `fix:` / `docs:` / `chore:`）
- 分支：`main` 永远可发布；功能分支 `feat/<scope>`；bugfix 分支 `fix/<issue>`

## AI 协同的工作哲学（写给 Kiro 自己）

用户来自的工作流是 **"定义问题 > AI 执行 > 人工校验"**。这意味着：

- 用户给问题描述时**期望被追问**，不要硬猜需求
- 用户给"做这个功能" 时**期望先看设计，再看代码**，不要直接堆代码
- 优先复用 PRD / ARCHITECTURE 里已有的决策，**不要重复发明**
- 如果某个请求与上面"不可妥协的产品决策"冲突，**先指出冲突再问怎么办**，不要默默执行

## 当前阶段

v0.1 文档刚成形（PRD + Architecture + Roadmap）。
工程代码：**0 行**。下一步通常是：
1. 创建 Rust workspace 骨架（M0）
2. fcitx5-synapse hello-world engine（M0）
3. gRPC protobuf 契约 v0
