# Synapse Nexus — 架构设计文档

- 版本：v0.1（草案，与 PRD v0.1 配套）
- 日期：2026-05-31
- 状态：DRAFT

> 本文档回答 PRD 不回答的 **怎么实现**。所有"做什么 / 为什么做"见 [PRD.md](./PRD.md)。

---

## 1. 设计原则（先于架构图）

按重要性排序，**前面的原则可以推翻后面的**：

1. **跨平台单一业务逻辑**  
   只能有一份业务逻辑（识别调度、Polish、计费、词库）。它必须能在 Linux / Windows / iOS 上跑。
2. **前端薄、后端厚**  
   每个平台前端只做三件事：音频采集、文本注入、UI。其它任何业务规则**不**进前端。
3. **Provider 抽象一切外部依赖**  
   ASR、Polish LLM、计费后端、本地兜底模型 —— 全部以 trait/接口 形式抽象。换供应商不应改业务代码。
4. **失败永远有路可走**  
   云端 ASR 挂了 → 本地兜底；Polish 挂了 → 用原始 ASR；本地兜底挂了 → 浮窗提示但**不**崩溃。
5. **延迟优先于精度**  
   能用 800ms 的差结果就不用 1.5s 的好结果（PRD §6 已锁死）。Polish 是 best-effort，**不能阻塞**输出。
6. **隐私优先于功能**  
   音频不持久化是不可妥协的。任何"为了调试方便保留一下"的设计直接拒。

---

## 2. 系统架构总览

### 2.1 进程模型

```
┌─────────────────────────────────────────────────────────────────┐
│                       目标应用（VSCode / Slack / ...）             │
│                              ▲                                    │
│                              │ 文本注入                           │
│                              │                                    │
│   ┌──────────────────────────┴──────────────────────┐            │
│   │     Platform Frontend（每平台一个，薄）         │            │
│   │   - Linux:  fcitx5 engine plugin (C++)          │            │
│   │   - Windows: TSF Text Service (C++)             │            │
│   │   - iOS:    Keyboard Extension (Swift)          │            │
│   │   职责：音频采集 + 文本注入 + 浮窗 UI            │            │
│   └──────────────────────────┬──────────────────────┘            │
│                              │ IPC (gRPC over Unix socket /       │
│                              │       XPC on iOS)                  │
└──────────────────────────────┼─────────────────────────────────────┘
                               │
        ┌──────────────────────▼────────────────────────┐
        │   synapsed (Rust core daemon, 跨平台)           │
        │   职责：识别调度、Polish、计费、词库、状态机      │
        │   ┌────────────────────────────────────────┐  │
        │   │  Session Manager                       │  │
        │   │  ├─ Audio Pipeline (cpal / on iOS:     │  │
        │   │  │   AVAudioEngine via FFI)            │  │
        │   │  ├─ ASR Provider (trait)               │  │
        │   │  │   ├─ DoubaoStreaming                │  │
        │   │  │   ├─ Paraformer / SenseVoice        │  │
        │   │  │   └─ LocalSherpaOnnx (fallback)     │  │
        │   │  ├─ Polish Provider (trait)            │  │
        │   │  │   ├─ QwenFlash                      │  │
        │   │  │   └─ OpenAI-Compatible (custom)     │  │
        │   │  ├─ Lexicon (system + user + dynamic)  │  │
        │   │  ├─ Billing & Quota (local + sync)     │  │
        │   │  └─ Telemetry (opt-in)                 │  │
        │   └────────────────────────────────────────┘  │
        └─────────────┬───────────────────┬─────────────┘
                      │                   │
              ┌───────▼─────┐    ┌────────▼────────┐
              │ ASR / LLM   │    │  Billing /      │
              │ Cloud APIs  │    │  Sync Backend   │
              └─────────────┘    └─────────────────┘
```

### 2.2 关键决策

| 决策 | 选择 | 替代方案 | 理由 |
|---|---|---|---|
| Core 语言 | **Rust** | C++ / Go | FFI 干净（cbindgen / uniffi），iOS 静态库友好，async 生态成熟，内存安全 |
| IPC 协议 | **gRPC（Linux/Windows）+ XPC（iOS）** | JSON-RPC, raw socket | gRPC 跨语言、有流式、契约明确；iOS 沙盒只能用 XPC |
| 音频库 | **cpal**（桌面）+ 平台原生（iOS） | PortAudio | cpal 是 Rust 原生，跨 ALSA/PulseAudio/PipeWire/CoreAudio/WASAPI |
| 流式协议（与云 ASR） | **WebSocket** | gRPC, HTTP chunked | 豆包 / 火山 / Aliyun 都是 WebSocket，不要发明轮子 |
| Linux IME 框架 | **Fcitx5 优先，IBus 兜底** | 只 Fcitx5 / 自己实现 | Fcitx5 API 干净，Wayland 支持好；IBus 是 GNOME 默认必须兜底 |
| Linux 显示协议 | **X11 + Wayland 双支持** | 只 X11 | Ubuntu 22.04+ 默认 Wayland；不能砍 |
| 包格式（Linux） | **.deb（Ubuntu）+ Flatpak（其它发行版）** | AppImage / Snap | Flatpak 沙盒模型与 IME 冲突需要 portal，但兼容性最广 |
| 配置存储 | **TOML 在 `~/.config/synapse-nexus/`** | JSON / SQLite | 人类可读，Rust 生态默认 |
| 本地数据 | **SQLite** | 纯文件 | 词库、历史、计费日志需要事务 |

---

## 3. Rust Core Daemon（`synapsed`）

### 3.1 Crate 结构

```
crates/
├── synapse-core/         # 业务逻辑：Session 状态机、调度
├── synapse-asr/          # ASR Provider trait + 各实现
│   ├── doubao/
│   ├── paraformer/
│   └── sherpa-local/
├── synapse-polish/       # Polish Provider trait + 各实现
│   ├── qwen/
│   └── openai-compat/
├── synapse-lexicon/      # 词库（system / user / dynamic）
├── synapse-billing/      # 计费与额度
├── synapse-ipc/          # gRPC server (tonic) + protobuf
├── synapse-audio/        # cpal 封装 + VAD（webrtc-vad）
├── synapse-config/       # TOML 配置
└── synapse-daemon/       # 二进制入口，把上面装配起来
```

### 3.2 核心 Provider trait（草案）

```rust
// synapse-asr/src/lib.rs
#[async_trait]
pub trait AsrProvider: Send + Sync {
    /// 开始一次流式会话。返回一个事件流：partial 文本、final 文本、错误。
    async fn start_session(
        &self,
        cfg: AsrConfig,
    ) -> Result<Box<dyn AsrSession>, AsrError>;
}

#[async_trait]
pub trait AsrSession: Send {
    /// 推一个音频帧（16kHz, 16-bit mono PCM, 推荐 20ms 一帧）
    async fn push_audio(&mut self, frame: &[i16]) -> Result<(), AsrError>;
    /// 拉下一个事件
    async fn next_event(&mut self) -> Option<AsrEvent>;
    /// 主动结束（如用户松开 push-to-talk）
    async fn finalize(self: Box<Self>) -> Result<String, AsrError>;
}

pub enum AsrEvent {
    Partial { text: String, confidence: f32 },
    Final { text: String, segment_id: u64 },
    Error(AsrError),
}
```

```rust
// synapse-polish/src/lib.rs
#[async_trait]
pub trait PolishProvider: Send + Sync {
    /// 给定原始 ASR + 上下文 + 词库，返回修正后文本。
    /// 实现必须遵守 budget（默认 600ms）。超时直接返回 Err，由调用方决定 fallback。
    async fn polish(&self, req: PolishRequest, budget: Duration) -> Result<String, PolishError>;
}

pub struct PolishRequest {
    pub raw: String,                    // ASR 原始结果
    pub context_before: String,         // 光标前 50 字
    pub active_lexicons: Vec<Lexicon>,  // 启用的词库
    pub user_corrections: Vec<Correction>, // 最近 50 条修正历史（FR-POLISH-05）
}
```

### 3.3 Session 状态机

一次"按住说话 → 松开 → 文字落到光标"是一个 Session。

```
                    push-to-talk
                       pressed
   ┌──────┐    ───────────────────►    ┌─────────┐
   │ Idle │                            │Recording│
   └──────┘    ◄───────────────────    └─────────┘
                  released / VAD             │
                                             │ first audio frame
                                             ▼
                                       ┌─────────────┐
                                       │ Recognizing │
                                       └─────────────┘
                                             │
                              ASR final text │
                                             ▼
                                       ┌──────────┐
                                       │Polishing │
                                       └──────────┘
                                             │
                                  done / timeout
                                             ▼
                                       ┌──────────┐
                                       │Committing│ ──► 写到目标应用 ──► Idle
                                       └──────────┘
```

每个状态都有超时和兜底：

| 状态 | 超时 | 失败动作 |
|---|---|---|
| Recording | 60s | 自动 finalize |
| Recognizing | 5s 无 partial | 切到 Local fallback |
| Polishing | 600ms | 跳过，直接用原始结果 |
| Committing | 100ms | 重试一次，失败则浮窗提示 |

### 3.4 Polish "差异审计"（应对风险 R2）

幻觉是这个产品的生死线之一。Polish 输出**必须**经过审计：

```rust
fn audit_polish(raw: &str, polished: &str) -> AuditResult {
    let edit_ratio = levenshtein(raw, polished) as f32 / raw.chars().count() as f32;
    let added_concepts = detect_added_named_entities(raw, polished);

    if edit_ratio > 0.30 {
        return AuditResult::Reject(Reason::TooMuchChange);
    }
    if !added_concepts.is_empty() {
        return AuditResult::Reject(Reason::HallucinatedEntities(added_concepts));
    }
    AuditResult::Accept
}
```

被拒的 Polish 结果**整段丢弃**，回退用原始 ASR。这个审计层是产品而非工程决策的一部分，所以放在 core 而非 provider 内。

---

## 4. 平台前端

### 4.1 Linux：fcitx5-synapse

- 语言：C++（fcitx5 是 C++ API）
- 体积目标：< 200 行有效代码
- 职责：
  1. 注册一个 `Engine`，实现 `keyEvent`（监听 `Super+Space`）
  2. 启动音频采集（fcitx5 没有这个 API，要直接用 PortAudio / pipewire client）— **改为：把音频采集放到 daemon 侧**，前端只发"开始 / 停止" RPC
  3. 收到 daemon 的 `Partial` 事件 → 用 `inputContext->updatePreedit()` 显示草稿
  4. 收到 `Final` → 用 `inputContext->commitString()` 注入

> **关键技术验证（M0 必做）**：Wayland 下 fcitx5 commitString 是否在所有 GTK / Qt / Electron 应用都正常工作？

### 4.2 Windows：synapse-tsf

- 语言：C++ / Win32 + COM
- TSF 接口：`ITfTextInputProcessor`, `ITfThreadMgrEventSink`, `ITfKeyEventSink`
- 注入文本：`ITfContext::InsertTextAtSelection`
- 与 daemon 通过 named pipe / gRPC over loopback

### 4.3 iOS：SynapseKeyboard

- 语言：Swift + Rust（uniffi 绑定）
- ⚠️ 关键限制：
  - Keyboard Extension 内存上限 ~70MB
  - 默认无网络访问，需要在 Info.plist 里 `RequestsOpenAccess = YES`，用户必须手动开启"完全访问"
  - 无后台音频
- 因此 iOS 版砍掉本地兜底（sherpa-onnx 模型 100MB+ 装不下），只做云端流式

### 4.4 跨平台一致性的强制契约

所有前端实现一个相同的 protobuf 服务（IPC 契约）：

```protobuf
service SynapseFrontend {
  // 前端 → daemon
  rpc StartSession(StartSessionRequest) returns (stream SessionEvent);
  rpc StopSession(StopSessionRequest) returns (StopSessionResponse);
  rpc PushAudio(stream AudioFrame) returns (PushAudioAck);

  // daemon → 前端（以 SessionEvent stream 形式 push）
}

message SessionEvent {
  oneof kind {
    PartialText partial = 1;
    FinalText  final   = 2;
    Error      error   = 3;
    Quota      quota   = 4;  // 实时额度更新
  }
}
```

只要前端实现了这个契约，daemon 不需要知道它跑在哪个平台上。

---

## 5. 数据存储

### 5.1 本地 SQLite schema（草案）

```sql
-- 用户词库
CREATE TABLE lexicon_entry (
  id INTEGER PRIMARY KEY,
  category TEXT NOT NULL,         -- 'code' | 'ai' | 'general' | 'user'
  pattern TEXT NOT NULL,          -- 错误形式（可选）
  replacement TEXT NOT NULL,      -- 正确形式
  weight REAL DEFAULT 1.0,
  source TEXT,                    -- 'system' | 'user' | 'dynamic'
  created_at TIMESTAMP
);

-- 用户修正历史（用于动态学习 FR-POLISH-05）
CREATE TABLE correction_log (
  id INTEGER PRIMARY KEY,
  session_id TEXT,
  raw_asr TEXT NOT NULL,
  polished TEXT,
  user_final TEXT NOT NULL,       -- 用户实际接受 / 改成的版本
  context_before TEXT,
  app_id TEXT,
  created_at TIMESTAMP
);

-- 计费日志
CREATE TABLE billing_event (
  id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL,
  characters INTEGER NOT NULL,
  cost_micros INTEGER,            -- 1e-6 元为单位，避免浮点
  asr_provider TEXT,
  polish_provider TEXT,
  reconciled BOOLEAN DEFAULT 0,   -- 是否已与服务端对账
  created_at TIMESTAMP
);
```

### 5.2 配置文件

`~/.config/synapse-nexus/config.toml`

```toml
[input]
mode = "push_to_talk"             # or "toggle"
hotkey = "Super+Space"
vad_silence_ms = 1200

[asr]
provider = "doubao"
fallback = "sherpa_local"

[polish]
provider = "qwen_flash"
budget_ms = 600
enabled_lexicons = ["code", "ai", "general"]

[privacy]
keep_history_days = 0             # 默认不保留
sensitive_apps = ["com.alipay.*", "com.icbc.*"]

[billing]
warn_threshold_chars = 100
```

---

## 6. 跨网络与 Provider 实现细节

### 6.1 豆包流式 ASR（Provider 示例）

实现：[`crates/synapse-asr/src/doubao/`](../crates/synapse-asr/src/doubao/)

- 协议：WebSocket，二进制消息，文档见 <https://www.volcengine.com/docs/6561/1354869>
- 帧大小：建议 20ms（16kHz / 16bit mono → 640 字节 / 帧）
- 鉴权：ARK API key 通过 `Authorization: Bearer ark-...`
- 帧格式：4 字节固定 header + 可选 4 字节序列号 + 4 字节 payload size (BE u32) + payload
- 支持 gzip 压缩响应（自动解压）
- 实现要点：
  - **永远 keep-alive 一条 ws 连接**（M1.4 计划），避免冷启动 TCP/TLS 握手（首字延迟杀手）
  - 心跳：30s 一次（M1.4）
  - 错误重连：指数退避 + jitter（M1.4）

#### 配置

环境变量：
- `SYNAPSE_DOUBAO_API_KEY=ark-...` (必填)
- `SYNAPSE_DOUBAO_ENDPOINT=...` (默认 `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel`)
- `SYNAPSE_DOUBAO_APP_ID=...` (可选)
- `SYNAPSE_DOUBAO_RESOURCE_ID=...` (可选)

#### 错误码映射

| Volc `code` 范围 | 映射到 `AsrError` |
|---|---|
| 45000001-45000999 | `Auth` |
| 45001001-45001999 | `QuotaExhausted` |
| 45100001-45100999 | `Timeout` |
| 其它非零 | `Protocol` |
| HTTP 401/403 (握手期) | `Auth` |
| HTTP 429 (握手期) | `QuotaExhausted` |

### 6.2 Polish（Qwen-Flash）

- 协议：OpenAI 兼容 HTTP（Chat Completions），`stream=false`
- Prompt 模板（v0，需迭代）：

```
你是一个中英文混合输入的修正器。修正下面的 ASR 结果中的错别字、专业术语、标点。
严格遵守：
1. 不得增加任何原文没有的语义信息。
2. 不得删除任何原文有的语义信息。
3. 中英文之间保持一个空格。
4. 编程相关术语优先使用以下词库：{LEXICON}
5. 用户最近的修正习惯：{USER_CORRECTIONS}

上下文（光标前）：{CONTEXT}
ASR 原文：{RAW}

直接输出修正后的文本，不要任何解释。
```

### 6.3 本地兜底：sherpa-onnx

- 模型：`sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20`
- 体积：~100MB（Ubuntu/Windows 默认装；iOS 不装）
- 精度差，仅用于网络故障兜底

---

## 7. 测试策略

| 层级 | 工具 | 覆盖目标 |
|---|---|---|
| 单元测试 | `cargo test` | core / lexicon / billing 业务逻辑 ≥ 80% |
| Provider 集成 | mock server + tokio-test | ASR / Polish 重连、超时、错误路径 |
| 端到端 | 自建 200 条评测语料 | CER / Polish 命中率 / 首字延迟 |
| Linux 前端 | xdotool 模拟按键 + dbus 验证 | fcitx5 集成 |
| 性能回归 | 每周跑评测集 | 延迟 / 准确率不能回退 |

评测语料组成（200 条，分层抽样）：
- 60 条：纯中文日常
- 40 条：纯英文（含编程术语）
- 60 条：中英混说（PRD §4.2 场景 A/B 那种）
- 20 条：含口头禅
- 20 条：噪声环境（咖啡厅 / 地铁背景）

---

## 8. 部署与发布

| 制品 | 平台 | 通道 |
|---|---|---|
| `synapse-nexus_<ver>.deb` | Ubuntu 22.04+ | 自建 apt 仓库 + 官网下载 |
| `synapse-nexus.flatpak` | 其它 Linux | Flathub（v1.1） |
| `synapse-nexus-setup.exe` | Windows 10+ | 官网下载 + 自动更新 |
| App Store IPA | iOS 16+ | App Store Connect |

发布流水线：

```
GitHub PR → CI (lint + test + 评测集回归)
         → main merge
         → tag v*
         → release workflow
            ├─ build .deb (cross 编译)
            ├─ build .flatpak
            ├─ build .exe (windows runner)
            └─ build .ipa (macos runner，需要签名密钥)
         → 发布到分发通道 + 公告
```

---

## 9. 安全

- **Daemon 不监听任何网络端口**，IPC 只走 Unix domain socket（权限 0600）
- 与云端通信全部 HTTPS / WSS，证书 pinning 在 v1.1 加上
- 用户 API key（如果用户接自己的 OpenAI 兼容端点）存在 OS keyring（Linux: Secret Service / Windows: DPAPI / iOS: Keychain）
- 计费对账签名（HMAC），防止用户篡改本地计费日志骗免费用量

---

## 10. 待解决的技术问题

- [ ] T1：Wayland 下 fcitx5 + Electron 应用（VSCode / Slack）的注入兼容性需在 M0 验证
- [ ] T2：iOS Keyboard Extension 70MB 内存上限下，Rust 静态库实际占用是多少？需 spike
- [ ] T3：Windows TSF 在 UWP 应用（如新版 Outlook）中的兼容性
- [ ] T4：豆包 WebSocket 的并发会话限制 / 提价风险，需要从商务侧确认
- [ ] T5：iOS 上 Polish 调用是否会被系统因为"键盘扩展不应大量发网络请求"而限速？

---

## 附录：跨平台代码占比预估

| 模块 | Rust core 占比 | 平台特定占比 |
|---|---|---|
| ASR / Polish / 计费 / 词库 / 状态机 | 100% | 0% |
| 音频采集 | 80%（cpal） | 20%（iOS 原生） |
| 文本注入 | 0% | 100%（每平台前端） |
| UI（浮窗 / 状态栏） | 30%（共享布局描述） | 70% |
| **整体** | **约 75%** | **约 25%** |

这是为什么 §1 第一条原则不能动 —— 跨平台 75% 复用是这个项目能做出来的全部前提。
