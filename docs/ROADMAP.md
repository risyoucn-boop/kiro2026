# Synapse Nexus — 路线图

- 版本：v0.1
- 日期：2026-05-31
- 状态：DRAFT

> 配套：[PRD.md](./PRD.md) §11、[ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 总体节奏

- **8 周到 v1.0 公开发布**（仅 Ubuntu）
- 单人开发节奏 + AI 协同工作流（详见 `.kiro/steering/product.md`）
- 每周一个可演示的增量；每个 milestone 结束都要能 demo 给一个真实用户看

```
周  1    2    3    4    5    6    7    8         12        20        32
   ├M0─┼─── M1 ───┼─M2─┼─M3─┼─── M4 ───┼─M5──── ▶ v1.1 ─── ▶ v1.2 ── ▶ v2.0
   地基 流式打通     Polish 计费    内测       公开    Windows  iOS    macOS
```

---

## M0 — 工程地基（第 1 周）

**目标**：可以在 Ubuntu 上跑通"按下快捷键 → fcitx5 调用 daemon → daemon 回一个写死的 'hello'"全链路。

### 交付物

- [ ] Rust workspace + 9 个 crate 骨架（见 ARCHITECTURE §3.1）
- [ ] `synapse-daemon` 二进制：监听 Unix socket，gRPC server (tonic) 启起来
- [ ] `fcitx5-synapse` C++ engine：注册成功，能在 fcitx5 配置面板看到
- [ ] gRPC protobuf 契约 v0：`StartSession` / `PushAudio` / `SessionEvent`
- [ ] CI：cargo fmt / clippy / test，CMake build for engine
- [ ] systemd user unit：`systemctl --user start synapsed`

### 退出标准（Definition of Done）

- 在 Ubuntu 22.04 X11 + 23.10 Wayland 各跑一遍：按住 `Super+Space` 在 gedit 里看到 `hello world` 被注入
- daemon 启动到 ready ≤ 1.5s
- `cargo test` 全绿，CI 全绿

### 关键技术验证（必须在本周完成）

- **TV-1（最高优先级）**：Wayland + fcitx5 + Electron（VSCode）的 commitString 兼容性。如果失败，整个 Ubuntu 战略要重新评估。
- **TV-2**：cpal 在 PipeWire 默认环境下抓 16kHz mono 是否稳定。

---

## M1 — 流式打通（第 2–3 周）

**目标**：豆包流式 ASR 接入，按住快捷键说话能实时看到中文文字流式出现。

### 第 2 周：ASR Provider

- [ ] `synapse-asr` 的 trait 实现 + `DoubaoStreaming` provider
- [ ] WebSocket 长连接 + 鉴权 + 心跳 + 重连
- [ ] `synapse-audio`：cpal 抓音频 → 重采样到 16kHz → VAD（webrtc-vad）
- [ ] daemon 端 Session 状态机（Idle / Recording / Recognizing）
- [ ] 内置评测脚本：跑 200 条评测语料，输出 CER 报告

### 第 3 周：流式渲染 + 浮窗

- [ ] fcitx5 前端：用 `updatePreedit` 显示草稿态、`commitString` 提交终态
- [ ] 浮窗指示器：录音中音量条 + 状态文字（用 Qt 或 GTK）
- [ ] 首字延迟埋点（本地 SQLite 记录）

### 退出标准

- 中文识别可日常用：评测集 CER ≤ 8%
- 首字延迟 P95 ≤ 1.5s（本地实测）
- 中英混说"打开 VSCode"能识别成"打开 VSCode"而不是"打开 V S Code"
- 网络中断时不崩溃（虽然此时还没本地兜底，至少要静默失败）

---

## M2 — Polish 接入（第 4 周）

**目标**：原始 ASR + Qwen-Flash Polish 双层架构跑通，编程术语命中率 ≥ 90%。

- [ ] `synapse-polish` trait + `QwenFlash` provider（OpenAI 兼容 API）
- [ ] Polish prompt 模板 v0（ARCHITECTURE §6.2）
- [ ] 三个内置词库：`code` / `ai` / `general`（每个 100–300 词，手工整理）
- [ ] 上下文抓取：Linux 下从 fcitx5 surrounding text API 拿光标前 50 字
- [ ] **差异审计**：edit_ratio > 30% 或新增命名实体 → 拒绝
- [ ] Polish budget 严格 600ms，超时直接放弃

### 退出标准

- 评测集 Polish 命中率 ≥ 90%（编程 / AI 词库）
- Polish 失败不影响输出（fallback 到原始 ASR）
- 端到端 P95 延迟（含 Polish）≤ 4 秒（5 秒语音）
- 抽 50 句人工审计：零幻觉（Polish 不该编造内容）

---

## M3 — 计费闭环（第 5 周）

**目标**：一个真实用户能完成"安装 → 用免费额度 → 充值 → 继续用"全流程。

- [ ] `synapse-billing`：本地按字数计费、SQLite 日志、HMAC 签名防篡改
- [ ] 状态栏图标：实时剩余字数（AppIndicator）
- [ ] 余额预警：≤ 100 字弹非阻塞通知
- [ ] 极简后端（FastAPI / Cloudflare Workers）：
  - [ ] 充值接口（占位，先用 Stripe Test 或微信扫码）
  - [ ] 用量上报与对账
  - [ ] 用户表（邮箱注册即可）
- [ ] 设置 UI（最小版）：API 端点 / 词库开关 / 快捷键

### 退出标准

- 内部 dogfooding：自己充 10 元，用一周用完
- 余额耗尽时自动降级到免费模式（标注，不再调云）
- 计费日志与服务端对账误差 < 0.1%

---

## M4 — 内测（第 6–7 周）

**目标**：50 个真实用户连续用一周，收集崩溃 / 误识别 / 不爽点。

### 第 6 周

- [ ] .deb 打包 + apt 仓库
- [ ] 官网（一个 landing page，用静态站）+ 下载 / 安装文档
- [ ] 用户协议 / 隐私政策（外审一遍）
- [ ] Crash report（用户同意后，用 Sentry / 自建）
- [ ] 邀请 50 个内测用户（V2EX、即刻、Twitter 中文圈，定向投放）

### 第 7 周

- [ ] Bug 修复 sprint
- [ ] 评测集回归
- [ ] 长尾场景修复：Wayland 特殊应用（Discord / Telegram / Obsidian）
- [ ] 用户反馈分类，决定 v1.0 是否需要新功能（**默认不加，只修 bug**）

### 退出标准

- DAU/MAU 比 ≥ 30%（内测期）
- 用户主动反馈崩溃 < 5 次
- NPS（小样本）≥ 30

---

## M5 — v1.0 公开发布（第 8 周）

**目标**：公开发布，付费通道全部打通。

- [ ] 充值通道生产化（微信 / 支付宝 / Stripe 三选二）
- [ ] 阶梯定价上线（10 / 50 / 200 元三档）
- [ ] 自动更新（基于 .deb 仓库 + apt）
- [ ] B 站 / 知乎 / Twitter 发布视频 + 文章
- [ ] GitHub 开源（核心 daemon 开源，前端可选；商业 polish prompt 不开源）

### 退出标准

- 公开发布日：至少 100 个独立 IP 下载
- 第一周：≥ 3 个付费用户
- 媒体：至少一篇技术博客 / 视频 1 万播放

---

## v1.1 — Windows 端（约第 12 周）

- [ ] `synapse-tsf` Text Service（C++/COM）
- [ ] Windows 安装包（NSIS / WiX）
- [ ] 使用 Linux 阶段已稳定的 daemon，零业务逻辑改动
- [ ] DPAPI 存储 API key
- [ ] CI 增加 Windows runner

**风险**：TSF 比 fcitx5 复杂得多，需要 1.5–2 周。

---

## v1.2 — iOS 端（约第 20 周）

- [ ] Rust core 用 uniffi 包成 .xcframework
- [ ] SynapseKeyboard Extension（Swift）
- [ ] 内存优化（≤ 70MB）
- [ ] App Store 审核（Privacy Manifest、Open Access 引导）
- [ ] 跨设备词库同步（端到端加密）

---

## v2.0 — macOS 端（约第 32 周）

- [ ] InputMethodKit 集成
- [ ] 与 iOS 共享前端代码
- [ ] Universal binary

---

## 不在路线图上的事（明确）

| 项 | 决策 |
|---|---|
| 自研 ASR 模型 | ❌ 永远不做 |
| 方言识别 | ❌ v2.0 前不做 |
| Android | ❌ v2.0 前不做 |
| 拼音 / 五笔 | ❌ 永远不做 |
| 离线优先模式 | ❌ 不做（兜底就够了） |
| 语音命令（"换行"、"删除"） | ⏸ v1.x 评估，v1.0 不做 |

---

## 节奏检查（Ritual）

- **每日**：commit；睡前自测一次完整链路
- **每周五**：跑评测集回归 + 写一篇周记（成功 / 失败 / 学到）
- **每个 milestone 结束**：demo 给一个真实用户看，记录 3 条最痛反馈
- **每两周**：复盘 PRD —— 哪些 P1 应该降到 P2？哪些假设被验证 / 证伪？
