# Real-machine validation guide

> 本文档教你怎么在你自己的 Ubuntu 机器上验证 Kiro 在沙盒里写不动的两件事：
>
> 1. **M1.3 Doubao 适配器**对真实 ARK API 是否真的能跑通
> 2. **TV-1**（PRD §13 Q1 已锁定为 v1.0 必交付）— Wayland + fcitx5 + Electron 的 `commitString` 兼容性
>
> 这两件事都需要"真机 + 真服务"，沙盒里不可能替你做。

---

## 0. 先决条件

### 0.1 你需要轮换的 ARK key

如果你之前在聊天里贴过 `ark-...` 形态的 key，**那条消息可能已经被多个系统记录**（浏览器历史、observability 日志等）。请：

1. 去 [ARK 控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey) **删除旧 key、生成一个新的**
2. 新 key **永远不要**贴进任何地方（聊天、issue、PR、README）；只放在你机器的 `.env`

### 0.2 工作环境

- Ubuntu 22.04 LTS 或更新（24.04 优先，Wayland 默认）
- Rust 1.85+（项目通过 `rust-toolchain.toml` 锁定 1.92）
- 一个 X11 会话和一个 Wayland 会话（GNOME 默认会话切换器在登录页面）

### 0.3 仓库就绪

```bash
git clone https://github.com/risyoucn-boop/kiro2026.git
cd kiro2026

# 拉所有未合并的特性分支以试用最新功能（按依赖顺序）
git fetch --all
git checkout feat/m1.3-doubao-adapter      # 最新一支，包含前面所有合并

# 复制环境变量模板，填入你的新 ARK key
cp .env.example .env
$EDITOR .env
# 至少改这两行：
#   SYNAPSE_ASR_PROVIDER=doubao
#   SYNAPSE_DOUBAO_API_KEY=ark-<你的新 key>
```

---

## Part 1 — 验证 M1.3 Doubao 适配器

### 1.1 启动 daemon，确认它装载了 doubao provider

```bash
set -a; source .env; set +a
cargo run -p synapse-daemon --bin synapsed
```

期望日志（关键字段是 `asr_provider=doubao`）：

```
INFO synapsed ready socket=/run/user/1000/synapse-nexus/synapsed.sock asr_provider=doubao
```

**如果看到 `asr_provider=mock`**：你 `.env` 没有正确加载。检查：
- `SYNAPSE_DOUBAO_API_KEY` 真的设上了？`echo $SYNAPSE_DOUBAO_API_KEY` 应该输出 `ark-...`
- 你是否漏了 `set -a; source .env; set +a` 这一步？（直接 `source .env` 不导出变量）

### 1.2 用一个最小客户端跑一次完整会话

我们的 IPC 协议是 gRPC over Unix socket。最快的验证方式是用 `grpcurl`。

#### 装 grpcurl

```bash
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
# 或 apt 装：sudo apt install grpcurl  （Ubuntu 24.04+）
```

#### 跑一次 StartSession

```bash
SOCKET=$XDG_RUNTIME_DIR/synapse-nexus/synapsed.sock

grpcurl -plaintext -unix \
  -import-path proto -proto proto/synapse/v0/synapse.proto \
  -d '{"client_id":"validate","app_context":"manual","context_before":""}' \
  $SOCKET synapse.v0.SynapseFrontend/StartSession
```

#### 期望输出

如果协议层一切正常（虽然没推音频，daemon 会等到你 ctrl-C 才知道音频结束），你应该看到：

- gRPC 连接立刻建立（不是 `connection refused`）
- daemon 端日志会有 `StartSession ... asr=doubao`
- daemon 内部尝试 ws connect 到 `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel`
- 如果 ARK key 有效且 endpoint 接受这个 key 形态，会握手成功；否则收到一个 `SessionEvent.Error` 帧

按 `Ctrl-C` 终止。

### 1.3 推一些音频，验证完整链路

如果上面 1.2 握手成功（没收到 Error 帧），下一步是推真音频。最简单的：用 `ffmpeg` 录一段小语音，再用 grpcurl 把 PCM 推给 PushAudio。

```bash
# 录 5 秒 16kHz mono PCM
ffmpeg -f alsa -i default -ar 16000 -ac 1 -t 5 -f s16le sample.pcm

# 把 PCM 切成 ~20ms 的块（每块 320 个 i16 = 640 字节）
# 这步可以写个简单的 Python 脚本生成 grpcurl 的 JSON 输入流
```

> ⚠️ grpcurl 推 client-streaming 二进制 payload 有点别扭。如果你愿意，我可以下一个 PR 加一个 `synapse-cli` 二进制工具，专门做这种"读 wav 文件、推到 daemon、打印事件"的事。说一声。

### 1.4 怎么读 daemon 日志

加详细日志：

```bash
RUST_LOG=synapse_asr=debug,synapsed=debug,info \
cargo run -p synapse-daemon --bin synapsed
```

关键 log 行：

| Log | 含义 |
|---|---|
| `synapsed ready ... asr_provider=doubao` | daemon 启起来了 |
| `StartSession client_id=...` | gRPC 调用到达 |
| `doubao ws connecting endpoint=wss://...` | 正在连 Volc |
| `asr error: AsrError::Auth` | API key 无效 → 检查 `.env` |
| `asr error: AsrError::Network(...)` | 网络问题 / endpoint 错 |
| `asr error: AsrError::Protocol(...)` | 协议层不匹配 → 见 1.5 |

### 1.5 协议层错误怎么办

我在沙盒里**没有**用真 Volc API 跑过，只跑过我自己写的 mock binary protocol server。所以 Volc 现在跑的版本可能在两个地方跟我的实现略有出入：

#### 1.5.1 JSON 配置 schema 可能不一样

如果你看到 daemon 日志里有形如 `server code XXX: <消息>` 的 Protocol error，**最大可能性**是 `build_config_payload` 里的 JSON 跟 Volc 期待的不匹配。

修法：编辑 [`crates/synapse-asr/src/doubao/mod.rs`](../crates/synapse-asr/src/doubao/mod.rs) 里的 `build_config_payload` 函数，按 Volc 当前文档调整字段。然后：

```bash
cargo build -p synapse-daemon
```

#### 1.5.2 可能需要额外的 auth 头

如果握手期就拿到 `AsrError::Auth`，但你确认 key 是新的、有效，可能 ARK 要求额外的头（比如 `X-Api-App-Key`）。

修法：在 `.env` 里加：

```
SYNAPSE_DOUBAO_APP_ID=<你 ARK 控制台的 App ID>
SYNAPSE_DOUBAO_RESOURCE_ID=<可选>
```

`DoubaoConfig` 已经支持，daemon 会自动把它们当作头送出去。

#### 1.5.3 endpoint 可能不对

`wss://openspeech.bytedance.com/api/v3/sauc/bigmodel` 是文档里给的 bigmodel 端点。如果你的 ARK 套餐是别的产品（流式/非流式/方言版），endpoint 不一样：

```bash
# .env
SYNAPSE_DOUBAO_ENDPOINT=wss://你查到的真 endpoint
```

### 1.6 验证完了告诉我什么

最有用的反馈格式（直接发给我或开 GitHub issue）：

```
1. ASR provider 启动是否正常： [是 / 否]
   - 日志里 asr_provider= 是什么？

2. StartSession + grpcurl 一次会话：
   - 收到的第一个事件是什么？(Partial / Final / Error)
   - 如果是 Error，code 和 message 分别是？
   - daemon 端 RUST_LOG=debug 时打的最后 5 行是？

3. 如果遇到 Protocol error：
   - 把那一段 JSON 配置 schema (build_config_payload 的输出) 跟 Volc 文档对一下
   - 把差异贴出来
```

---

## Part 2 — TV-1：Wayland + fcitx5 + Electron commitString 验证

PRD §13 Q1 已经锁定 Wayland 进 v1.0，TV-1 不能跳过。如果验证失败，**不要砍 Wayland**，开 issue 标 `tv-1`，由我探索 fallback 路径。

### 2.1 装 fcitx5 + 构建依赖

```bash
sudo apt update
sudo apt install -y \
  fcitx5 fcitx5-frontend-gtk3 fcitx5-frontend-gtk4 fcitx5-frontend-qt5 \
  libfcitx5core-dev libfcitx5utils-dev libfcitx5config-dev \
  extra-cmake-modules cmake build-essential

# 让 fcitx5 在登录后自启
sudo apt install -y fcitx5-config-qt
```

确保系统级 input method 设成 fcitx5：

```bash
im-config -n fcitx5
# 注销 / 重新登录
```

### 2.2 构建并安装 synapse-fcitx5 engine

```bash
cd kiro2026/frontends/linux-fcitx5

cmake -S . -B build
cmake --build build -j

# 装到系统目录
sudo cmake --install build

# 让 fcitx5 重新扫描 addons
fcitx5 -r
```

### 2.3 在 fcitx5 配置里启用 Synapse Nexus

```bash
fcitx5-configtool
```

在配置面板：
1. 取消勾选 "Only Show Current Language"（不然中文输入法不一定显示）
2. 在 "Available Input Method" 列表里找 **Synapse Nexus**
3. 双击或点 `<` 加到 "Current Input Method"
4. Apply

### 2.4 启动 daemon（会被 engine 通过 gRPC 调用 — **此功能在 PR-C 里**）

⚠️ **重要**：截至 M1.3，**fcitx5 engine 还没接 daemon 的 gRPC**（C++ 端的 grpc++ 客户端是我接下来要做的 PR-C）。当前 M0 状态下 engine 就是按 Super+Space 直接 commitString("hello world")，不打 RPC。

也就是说，**你现在能跑的是"engine 注册成功 + commitString 注入路径在你的桌面环境上是否工作"**——这正是 TV-1 要验的事。完整链路（engine → daemon → ASR → 文字）等 PR-C 合了再做端到端测试。

### 2.5 跑 TV-1 测试矩阵

切到 Synapse Nexus（一般 Super+Space 切输入法，或托盘点 fcitx5 图标），然后在每个目标应用里**按住 `Super+Space`**（engine 的 hotkey），看是否出现 `hello world`。

#### X11 会话

| 应用 | 期望 | 验证 |
|---|---|---|
| `gedit` | `hello world` 落到光标 | □ |
| `xterm` | 同上（控制台） | □ |
| `vscode --disable-features=UseOzonePlatform` | 同上 | □ |
| Firefox 地址栏 | 同上 | □ |
| `slack` 桌面版 | 同上 | □ |

#### Wayland 会话

| 应用 | 期望 | 验证 |
|---|---|---|
| `gnome-text-editor` | `hello world` 落到光标 | □ |
| `kate`（Qt6） | 同上 | □ |
| `code --enable-wayland-ime`（VSCode）| 同上 | □ |
| Firefox（Wayland） | 同上 | □ |
| Slack / Discord（Electron） | 同上 | □ |
| `kitty` / `alacritty` 终端 | 同上 | □ |
| `obsidian` | 同上 | □ |

#### 已知坑

- **VSCode (Electron) Wayland**：必须加 `--enable-wayland-ime` 启动，否则 IM 完全不工作。Issue: [microsoft/vscode#187338](https://github.com/microsoft/vscode/issues/187338)
- **Chromium / Chrome / Edge / Slack / Discord**：现代 Electron 默认 Ozone-Wayland，但 IM 支持有版本差异。如果挂了，试 `--ozone-platform=wayland --enable-wayland-ime`。
- **Firefox Wayland**：环境变量 `MOZ_ENABLE_WAYLAND=1`。
- **快捷键冲突**：GNOME 默认把 Super+Space 抢去切输入法。要么改 fcitx5 的 hotkey（`fcitx5-configtool` → Global Options → Trigger），要么改 GNOME 的（`Settings → Keyboard → ...`）。M1 完成后 hotkey 会从配置文件读，目前是写死 `Super+Space`。

### 2.6 反馈模板

请你把验证结果填回来（或直接贴在 PR #15 的 review 评论里）：

```
=== TV-1 报告 ===

桌面环境: [Ubuntu 22.04 / 24.04]
显示协议会话: [X11 / Wayland]
GNOME / KDE / Cinnamon: [...]

X11 会话结果:
  gedit:        ✅ / ❌ <现象>
  vscode:       ✅ / ❌ <现象>
  firefox:      ✅ / ❌ <现象>
  slack:        ✅ / ❌ <现象>

Wayland 会话结果:
  gnome-text-editor: ✅ / ❌
  vscode --enable-wayland-ime: ✅ / ❌
  firefox (MOZ_ENABLE_WAYLAND=1): ✅ / ❌
  slack:        ✅ / ❌
  obsidian:     ✅ / ❌

挂掉的应用，最具体的失败现象（只有一个 → 就够开工了）：
  ...

fcitx5 -d -r 输出（如果挂了，加 RUST_LOG=debug 再粘 daemon 日志）：
  ...
```

如果 80% 的应用挂在 Wayland 上 → 我们要做 IBus 协议 fallback（一周左右）。
如果只有 Electron 挂 → 等 PR-C 完了我们做 wlroots virtual-keyboard fallback（短）。
如果几乎都通 → 我们继续按计划做 PR-C，TV-1 通过。

---

## Part 3 — 验证完之后

把 Part 1 + Part 2 的结果贴回来。我会根据你的实际情况：

1. 如果 Doubao 协议层有 mismatch → 我做 fix PR
2. 如果 TV-1 在 Wayland 大面积挂 → 我做 fallback PR（IBus 路径或 virtual-keyboard 路径）
3. 如果一切顺利 → 我们继续 M2（Polish 层）和 PR-C（engine 接 daemon）

> ⚠️ **再次提醒**：你 ARK key 千万不要在反馈里粘进来。如果需要贴 daemon 日志，先 `sed` 掉所有 `ark-...`：
> ```bash
> RUST_LOG=debug ./synapsed 2>&1 | sed -E 's/ark-[a-zA-Z0-9-]+/ark-REDACTED/g' | tee daemon.log
> ```
