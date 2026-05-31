# Synapse Nexus

> 中英文混说语音输入法 · Ubuntu 优先 · 跨平台 · 按量付费

**状态：🚧 M1.2 进行中 — daemon 走通流式 WebSocket ASR 全链路（含 Bearer auth）**

Synapse Nexus（中文名"言枢"待定）是一款面向开发者与知识工作者的中英文混说语音输入法。
让"想到 → 说出 → 落到光标处"在 1.5 秒内完成。

## 当前可跑的

```sh
# 不带配置 — 用 Mock provider 演示流式 partial → final
cargo run -p synapse-daemon --bin synapsed

# 接真实 WebSocket ASR 后端（必须实现 Synapse Streaming ASR v0 协议）
SYNAPSE_ASR_ENDPOINT=wss://your-asr.example.com/v0 \
SYNAPSE_ASR_TOKEN=...                              \
cargo run -p synapse-daemon --bin synapsed
```

详细的 v0 流式控制协议见 [`crates/synapse-asr/src/streaming.rs`](./crates/synapse-asr/src/streaming.rs) 顶部 docstring。

## 仓库结构

```
.
├── Cargo.toml                         # workspace
├── proto/synapse/v0/synapse.proto     # IPC 契约 v0（gRPC）
├── crates/
│   ├── synapse-core/                  # session 状态机
│   ├── synapse-asr/                   # ASR Provider trait
│   ├── synapse-polish/                # Polish + 幻觉差异审计
│   ├── synapse-lexicon/               # 词库
│   ├── synapse-billing/               # 本地按量计费
│   ├── synapse-audio/                 # 音频采集（M1 接 cpal）
│   ├── synapse-config/                # 平台路径 / 配置
│   ├── synapse-ipc/                   # tonic-build 编译 proto
│   └── synapse-daemon/                # synapsed 二进制
├── frontends/linux-fcitx5/            # Fcitx5 engine（CMake / C++17）
├── packaging/systemd/synapsed.service # 用户级 systemd unit
└── docs/                              # PRD / ARCHITECTURE / ROADMAP
```

## 关键特性（计划中）

- 🎙️ **流式优先**：首字延迟 P95 ≤ 1.5s
- 🌏 **中英混说零切换**：`打开 Cursor 写一个 fetch 请求` 一次出对
- 🪞 **双层校验**：原始 ASR + LLM Polish + 差异审计（防幻觉）
- 💰 **按量付费**：1000 字免费试用，按字数计费，反订阅制
- 🧠 **动态学习**：分析最近 50 次修正历史，自动生成修正规则
- 🐧 **Ubuntu 优先**：v1.0 完整支持 fcitx5（X11 + Wayland）

## 平台路线图

| 平台 | 阶段 | ETA |
|---|---|---|
| Ubuntu (Fcitx5) | v1.0 | 第 8 周 |
| Windows (TSF) | v1.1 | 第 12 周 |
| iOS (Keyboard Extension) | v1.2 | 第 20 周 |
| macOS (InputMethodKit) | v2.0 | 第 32 周 |

## 文档

- 📋 [PRD（产品需求文档）](./docs/PRD.md) — 做什么 / 为什么 / 成功标准
- 🏗️ [ARCHITECTURE（架构设计）](./docs/ARCHITECTURE.md) — Rust core daemon + 平台前端
- 🗺️ [ROADMAP（路线图）](./docs/ROADMAP.md) — 8 周到 v1.0
- 🤖 [.kiro/steering/product.md](./.kiro/steering/product.md) — 项目背景与工作约定（给 AI / 协作者读）

## 技术栈预览

- **Core daemon**：Rust（cpal 音频、tonic gRPC、tokio async）
- **Linux 前端**：Fcitx5 engine（C++17）
- **Windows 前端**：TSF Text Service（C++/COM）
- **iOS 前端**：Keyboard Extension（Swift + Rust 静态库 via uniffi）
- **ASR**：豆包流式（首选）/ Paraformer / SenseVoice / 本地 sherpa-onnx 兜底
- **Polish**：Qwen-Flash / OpenAI 兼容端点

## 设计原则（精简版）

1. 跨平台单一业务逻辑（Rust core）
2. 前端薄、后端厚
3. 一切外部依赖 Provider trait 抽象
4. 失败永远有路可走
5. **延迟优先于精度**
6. **隐私优先于功能**

完整原则见 [ARCHITECTURE.md §1](./docs/ARCHITECTURE.md)。

## 不做什么（明确）

- ❌ 订阅制
- ❌ 离线纯本地识别（仅兜底）
- ❌ 方言识别
- ❌ 自研 ASR / LLM 模型
- ❌ 拼音 / 五笔等综合输入

## License

待定（核心 daemon 计划开源；商业 prompt 与品牌素材保留）。
