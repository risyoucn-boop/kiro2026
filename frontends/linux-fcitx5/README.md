# synapse-fcitx5

Synapse Nexus's Fcitx5 input method engine.

## M0 scope

- Registers as a Fcitx5 input method addon
- Hotkey `Super+Space` commits the literal string `hello world` (proof of
  injection path, both X11 and Wayland)
- **No IPC to `synapsed` yet** — that is the next commit

## Build

```sh
sudo apt install -y \
    cmake extra-cmake-modules \
    fcitx5 libfcitx5core-dev libfcitx5utils-dev libfcitx5config-dev
cmake -S . -B build
cmake --build build -j
sudo cmake --install build
```

After install:

```sh
fcitx5 -r          # reload addons
# Then: Configure → Input Method → Add → "Synapse Nexus"
```

## Verify Wayland TV-1

ROADMAP M0 TV-1 requires verifying `commitString()` works in Electron apps
under Wayland. After installing:

1. Switch to "Synapse Nexus" in fcitx5 tray
2. Open VSCode (run as `code --enable-wayland-ime`) and a GTK app
3. Press `Super+Space` in each — verify "hello world" lands at cursor

If VSCode injection fails, do **not** drop Wayland (PRD §13 Q1 has it as a
v1.0 must-have). Open an issue tagged `tv-1` and explore fallback paths
(IBus protocol shim or wlroots virtual-keyboard).
