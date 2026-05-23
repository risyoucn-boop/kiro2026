"""生成「图标检索目录」Excel:每行 1 个图标,内嵌 3 色缩略图,
支持表头筛选、关键词检索、文件路径直读。

xlsx 在这套里的角色 = 检索/速查目录,不是改色工具(改色请用 SVG + Impress/Draw)。
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import re

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from PIL import Image

from icons import COLORS, ICONS

ROOT = Path(__file__).resolve().parent.parent
PNG_DIR = ROOT / "build" / "png"
SVG_DIR_REL = "assets/svg"
OUT_XLSX = ROOT / "build" / "icon_library.xlsx"

# 单元格里展示的缩略图尺寸 (像素)
THUMB_PX = 80
ROW_HEIGHT_PT = 66  # ~88px
COL_WIDTHS = {
    "A": 5,    # 编号
    "B": 12,   # 分组
    "C": 14,   # 中文名
    "D": 28,   # 关键词(中英文 + 同义词)
    "E": 12,   # 深蓝灰图
    "F": 12,   # 品牌橙图
    "G": 12,   # 警示红图
    "H": 36,   # SVG 文件路径
    "I": 32,   # Iconify ID
}
HEADER = [
    "#", "分组", "中文名", "关键词",
    "深蓝灰", "品牌橙", "警示红",
    "SVG 文件路径", "Iconify ID",
]
COLOR_SLUGS = {"深蓝灰": "blue", "品牌橙": "orange", "警示红": "red"}

# 8 组的浅色背景(让分组在表里一眼可见)
GROUP_COLORS = {
    "导航与界面": "EAF2F8",  # 浅蓝
    "用户与账户": "F4ECF7",  # 浅紫
    "数据与报表": "E8F8F5",  # 浅青
    "通信与协作": "FEF9E7",  # 浅黄
    "文件与文档": "FDF2E9",  # 浅橙
    "状态与反馈": "FDEDEC",  # 浅红
    "商务与交易": "EBF5FB",  # 浅天蓝
    "系统与运维": "F4F6F7",  # 浅灰
}


def _resize_thumb(src: Path, size: int) -> Path:
    cache_dir = ROOT / "build" / "thumbs"
    cache_dir.mkdir(parents=True, exist_ok=True)
    dst = cache_dir / f"{src.stem}__{size}.png"
    if not dst.exists():
        with Image.open(src) as im:
            im = im.convert("RGBA")
            im.thumbnail((size, size), Image.LANCZOS)
            canvas = Image.new("RGBA", (size, size), (255, 255, 255, 0))
            canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
            canvas.save(dst, "PNG")
    return dst


def _build_keywords(group: str, name_zh: str, icon_id: str) -> str:
    """生成一行可被 Ctrl+F 搜到的关键词,中英文都覆盖。"""
    base = icon_id.split(":", 1)[1]
    eng_tokens = re.split(r"[-_]", base)
    semantic = [t for t in eng_tokens if t not in {"outline", "rounded", "sharp", "filled"}]
    eng = " ".join(eng_tokens)
    semantic_str = " ".join(semantic)
    parts = [name_zh, group, semantic_str, eng]
    seen, out = set(), []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return " · ".join(out)


def build():
    wb = Workbook()
    ws = wb.active
    ws.title = "图标检索"

    thin = Side(style="thin", color="DDDDDD")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ---- 表头 ----
    header_fill = PatternFill("solid", fgColor="2C3E50")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    for col_idx, title in enumerate(HEADER, 1):
        cell = ws.cell(row=1, column=col_idx, value=title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
    for col_letter, color_name in zip(["E", "F", "G"], ["深蓝灰", "品牌橙", "警示红"]):
        c = ws[f"{col_letter}1"]
        c.fill = PatternFill("solid", fgColor=COLORS[color_name].lstrip("#"))

    for col, width in COL_WIDTHS.items():
        ws.column_dimensions[col].width = width
    ws.row_dimensions[1].height = 28

    # ---- 数据行 ----
    for idx, (group, name_zh, icon_id) in enumerate(ICONS, 1):
        row = idx + 1
        ws.row_dimensions[row].height = ROW_HEIGHT_PT
        seq = f"{idx:02d}"
        keywords = _build_keywords(group, name_zh, icon_id)
        svg_path_template = f"{SVG_DIR_REL}/{{color}}/{seq}_{name_zh}.svg"

        ws.cell(row=row, column=1, value=idx).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row, column=2, value=group).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row, column=3, value=name_zh).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row, column=4, value=keywords).alignment = Alignment(
            horizontal="left", vertical="center", indent=1, wrap_text=True
        )
        ws.cell(row=row, column=4).font = Font(size=9, color="666666")
        ws.cell(row=row, column=8, value=svg_path_template).alignment = Alignment(
            horizontal="left", vertical="center", indent=1
        )
        ws.cell(row=row, column=8).font = Font(name="Consolas", size=9, color="333333")
        ws.cell(row=row, column=9, value=icon_id).alignment = Alignment(
            horizontal="left", vertical="center", indent=1
        )
        ws.cell(row=row, column=9).font = Font(name="Consolas", size=9, color="555555")

        # 嵌缩略图
        slug = icon_id.replace(":", "__").replace("/", "_")
        for col_idx, color_name in zip([5, 6, 7], ["深蓝灰", "品牌橙", "警示红"]):
            color_slug = COLOR_SLUGS[color_name]
            png = PNG_DIR / f"{slug}__{color_slug}.png"
            thumb = _resize_thumb(png, THUMB_PX)
            img = XLImage(str(thumb))
            img.width = THUMB_PX
            img.height = THUMB_PX
            ws.add_image(img, f"{get_column_letter(col_idx)}{row}")

        # 边框
        for col_idx in range(1, len(HEADER) + 1):
            ws.cell(row=row, column=col_idx).border = border

        # 分组色带:除图标列(5/6/7)外都涂分组色
        group_color = GROUP_COLORS.get(group, "FAFAFA")
        stripe = PatternFill("solid", fgColor=group_color)
        for col_idx in [1, 2, 3, 4, 8, 9]:
            ws.cell(row=row, column=col_idx).fill = stripe

    # ---- 表头筛选(autoFilter) + 冻结首行 ----
    last_col = get_column_letter(len(HEADER))
    last_row = len(ICONS) + 1
    ws.auto_filter.ref = f"A1:{last_col}{last_row}"
    ws.freeze_panes = "A2"

    # ---- 第二张:使用说明 ----
    ws2 = wb.create_sheet("使用说明")
    ws2["A1"] = "图标库使用说明"
    ws2["A1"].font = Font(bold=True, size=16, color="2C3E50")
    ws2.row_dimensions[1].height = 28

    notes = [
        "",
        "▎ 这个文件的角色",
        "  这是一个『检索目录』。用来浏览、搜索、定位图标,但不能在 Excel/Calc 里改图标颜色",
        "  (Excel 单元格里嵌入的是 PNG 位图,本质上没法用『填充』按钮改图)",
        "",
        "▎ 怎么找图标",
        "  方式 1:点表头任一列的下拉箭头,按【分组】或【中文名】筛选",
        "  方式 2:Ctrl+F 关键词搜索,『关键词』列已经包含中英文 + 同义词",
        "",
        "▎ 找到后怎么用",
        "  1. 看『SVG 文件路径』列,把 {color} 换成 blue / orange / red",
        "     例:assets/svg/blue/01_首页.svg",
        "  2. 直接拖这个 SVG 文件进 PPT/Word/Notion/Figma 都能用",
        "",
        "▎ 怎么改色",
        "  这个 xlsx 里的图是 PNG,改不了色。改色用这两条路:",
        "  • 用 LibreOffice Draw 打开 SVG:右键 → 区域 → 改色 → 导出",
        "  • 用 LibreOffice Impress 打开 icon_library.pptx:选图标 → 转为多边形 → 区域改色",
        "",
        "▎ 三色版本",
        f"  深蓝灰 {COLORS['深蓝灰']} (主用色)",
        f"  品牌橙 {COLORS['品牌橙']} (强调色)",
        f"  警示红 {COLORS['警示红']} (警示色)",
        f"  3 列已预渲染好,直接选对应色那张图复制走也行。",
        "",
        "▎ 分组分布",
    ]
    from collections import Counter
    counts = Counter(g for g, _, _ in ICONS)
    for g, n in counts.items():
        notes.append(f"  {g}: {n}")
    notes.append("")
    notes.append(f"▎ 总计 {len(ICONS)} 个图标 × 3 色 = 300 个 SVG / 300 张 PNG")

    for i, line in enumerate(notes, 2):
        ws2.cell(row=i, column=1, value=line).font = Font(size=11, color="333333")

    ws2.column_dimensions["A"].width = 80

    wb.active = 0

    OUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_XLSX)
    print(f"Excel 已生成: {OUT_XLSX} ({OUT_XLSX.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
