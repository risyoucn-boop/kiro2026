# Icon Library Generator

一键产出 1000 个可改色 PPTX 图标 + Excel 检索表 + 1000 个 SVG 文件。

## 安装

```bash
pip install python-pptx openpyxl lxml cairosvg
# cairosvg 仅用于生成预览图，不是必需
```

## 运行

```bash
python build.py
```

输出位于 `../output/`：

- `PPT图标语义库_可改色形状_1000.pptx`
- `PPT图标语义库_可改色形状_1000_检索表.xlsx`
- `PPT图标语义库_可改色形状_1000_索引.csv`

以及 `../icons_svg/` 下的 1000 个 .svg 文件。

## 模块依赖图

```text
build.py
  └─ registry.py          (基础 × 徽章 → 1000 个 IconDef)
       ├─ bases.py        (12 个分类 × ~14 个基础概念 = 169 个 base)
       │    └─ builders.py  (rect / circle / star / gear / arrow / shield / robot ...)
       │         └─ primitives.py  (normalize / scale / translate / 路径变换)
       └─ modifiers.py    (16 种角标徽章 + with_badge 装饰器)
```

## 扩展新图标

1. 在 `builders.py` 写一个新形状函数，返回 `list[part dict]`
2. 在 `bases.py` 把它加到对应分类的 `*_BASES` 列表里：
   ```python
   ("my_icon", "中文名", "EnglishName",
    lambda: my_new_shape_function(),
    "隐喻含义说明", "建议用法说明",
    ["关键词1", "关键词2"], ["en1", "en2"]),
   ```
3. 重跑 `build.py`，会自动出现 1 个 base + 5 个徽章变体 = 6 个新图标

## 扩展新徽章

1. 在 `modifiers.py` 写 `_my_badge(cx, cy)` 函数
2. 加到 `BADGES = {...}` 注册表里，附中英文标签
3. 在 `bases.py` 的 `CATEGORY_BADGES` 里把新徽章 key 加到相关分类
4. 重跑 `build.py`
