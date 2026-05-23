# 图标库 · 100 选 · 三色对照

精选 100 个 Material Symbols 图标,按 8 大业务场景分组,每个图标渲染 3 种主色 (深蓝灰 / 品牌橙 / 警示红) 的 256×256 PNG,产出可直接复用的 Excel 与 PPTX。

## 交付产物

| 文件 | 说明 | 大小 |
| --- | --- | --- |
| [`assets/icon_library.xlsx`](./assets/icon_library.xlsx) | 每行 1 个图标,内嵌 3 色缩略图 + 编号 / 中文名 / 分组 / Iconify ID | ~940 KB |
| [`assets/icon_library.pptx`](./assets/icon_library.pptx) | 16:9 幻灯片,封面 + 每组分页 (一页 12 图,图标 1.5×) + 三色对照页 | ~590 KB |
| [`assets/preview_grid.png`](./assets/preview_grid.png) | 100 个图标的网格静态预览 (深蓝灰主色) | ~300 KB |
| [`assets/preview_tricolor.png`](./assets/preview_tricolor.png) | 各组代表图标的三色对照 | ~92 KB |

### 网格预览 (深蓝灰主色)

![网格预览](./assets/preview_grid.png)

### 三色对照

![三色对照](./assets/preview_tricolor.png)

## 设计要点

- **覆盖密度**:8 个业务分组共 100 个图标,经过精选去重,Iconify ID 保证唯一。
  - 导航与界面 15 · 用户与账户 12 · 数据与报表 15 · 通信与协作 12
  - 文件与文档 12 · 状态与反馈 12 · 商务与交易 12 · 系统与运维 10
- **三色方案**:
  - 深蓝灰 `#2C3E50` — 主用色
  - 品牌橙 `#E67E22` — 强调色
  - 警示红 `#C0392B` — 警示色
- **Excel**:每行内嵌 80px 缩略图,三色横向排列,可直接复制单元格图片到设计稿。
- **PPTX**:一页 12 图,卡片化布局,图标尺寸 1.2 英寸 (上一版 0.8 英寸的 1.5×),中文名 + iconify 名一目了然。

## 重新构建

```bash
python3 -m venv .venv
.venv/bin/pip install openpyxl python-pptx Pillow cairosvg requests

# 1. 拉取 SVG,渲染 100 图 × 3 色 = 300 张 PNG (build/png/)
.venv/bin/python scripts/render.py

# 2. 生成 Excel
.venv/bin/python scripts/build_xlsx.py

# 3. 生成 PPTX
.venv/bin/python scripts/build_pptx.py

# 4. 生成静态预览 PNG (需要中文字体,Linux 下:dnf install google-noto-sans-cjk-fonts)
.venv/bin/python scripts/build_preview.py
```

## 数据来源

- 图标:[Material Symbols](https://github.com/google/material-design-icons) (Apache 2.0),通过 [Iconify API](https://iconify.design/docs/api/) 拉取
- 字体 (预览图渲染):Noto Sans CJK
