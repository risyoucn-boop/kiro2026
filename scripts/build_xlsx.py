"""生成 Excel 图标库:每行 1 个图标,内嵌 3 色缩略图 + 编号/中文名/分组/iconify ID。"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from PIL import Image

from icons import COLORS, ICONS

ROOT = Path(__file__).resolve().parent.parent
PNG_DIR = ROOT / "build" / "png"
OUT_XLSX = ROOT / "build" / "icon_library.xlsx"

# 单元格里展示的缩略图尺寸 (像素)
THUMB_PX = 80
ROW_HEIGHT_PT = 66  # ~88px
COL_WIDTHS = {
    "A": 6,    # 编号
    "B": 12,   # 分组
    "C": 14,   # 中文名
    "D": 14,   # 深蓝灰图
    "E": 14,   # 品牌橙图
    "F": 14,   # 警示红图
    "G": 38,   # iconify ID
}
HEADER = ["#", "分组", "中文名", "深蓝灰", "品牌橙", "警示红", "Iconify ID"]
COLOR_SLUGS = {"深蓝灰": "blue", "品牌橙": "orange", "警示红": "red"}
COLOR_HEX = COLORS  # 用于表头着色


def _resize_thumb(src: Path, size: int) -> Path:
    """生成缩略图副本,避免 openpyxl 直接嵌入大图。"""
    cache_dir = ROOT / "build" / "thumbs"
    cache_dir.mkdir(parents=True, exist_ok=True)
    dst = cache_dir / f"{src.stem}__{size}.png"
    if not dst.exists():
        with Image.open(src) as im:
            im = im.convert("RGBA")
            im.thumbnail((size, size), Image.LANCZOS)
            # 保证正方形画布,避免行高/列宽偏差
            canvas = Image.new("RGBA", (size, size), (255, 255, 255, 0))
            canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
            canvas.save(dst, "PNG")
    return dst


def build():
    wb = Workbook()
    ws = wb.active
    ws.title = "Icons (100)"

    thin = Side(style="thin", color="DDDDDD")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # 表头
    header_fill = PatternFill("solid", fgColor="2C3E50")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    for col_idx, title in enumerate(HEADER, 1):
        cell = ws.cell(row=1, column=col_idx, value=title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
    # 表头里把"深蓝灰/品牌橙/警示红"涂成对应颜色 (前景白)
    for col_letter, color_name in zip(["D", "E", "F"], ["深蓝灰", "品牌橙", "警示红"]):
        c = ws[f"{col_letter}1"]
        c.fill = PatternFill("solid", fgColor=COLOR_HEX[color_name].lstrip("#"))

    # 列宽 / 表头行高
    for col, width in COL_WIDTHS.items():
        ws.column_dimensions[col].width = width
    ws.row_dimensions[1].height = 28

    # 数据行
    for idx, (group, name_zh, icon_id) in enumerate(ICONS, 1):
        row = idx + 1
        ws.row_dimensions[row].height = ROW_HEIGHT_PT

        ws.cell(row=row, column=1, value=idx).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row, column=2, value=group).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row, column=3, value=name_zh).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row, column=7, value=icon_id).alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.cell(row=row, column=7).font = Font(name="Consolas", size=10, color="555555")

        slug = icon_id.replace(":", "__").replace("/", "_")
        for col_idx, color_name in zip([4, 5, 6], ["深蓝灰", "品牌橙", "警示红"]):
            color_slug = COLOR_SLUGS[color_name]
            png = PNG_DIR / f"{slug}__{color_slug}.png"
            thumb = _resize_thumb(png, THUMB_PX)
            img = XLImage(str(thumb))
            img.width = THUMB_PX
            img.height = THUMB_PX
            anchor_cell = f"{get_column_letter(col_idx)}{row}"
            # 用 anchor 让图片随单元格居中
            ws.add_image(img, anchor_cell)

        # 给每个单元格加边框
        for col_idx in range(1, len(HEADER) + 1):
            ws.cell(row=row, column=col_idx).border = border

        # 隔行底色 (除图片列外)
        if idx % 2 == 0:
            stripe = PatternFill("solid", fgColor="FAFAFA")
            for col_idx in [1, 2, 3, 7]:
                ws.cell(row=row, column=col_idx).fill = stripe

    # 冻结首行
    ws.freeze_panes = "A2"

    # 第二张表:概览统计
    ws2 = wb.create_sheet("Overview")
    ws2["A1"] = "图标库总览"
    ws2["A1"].font = Font(bold=True, size=14)
    ws2["A3"] = "总图标数"
    ws2["B3"] = len(ICONS)
    ws2["A4"] = "颜色变体"
    ws2["B4"] = " / ".join(f"{n} ({h})" for n, h in COLORS.items())
    ws2["A5"] = "缩略图尺寸"
    ws2["B5"] = f"{THUMB_PX}px (源图 256px)"
    ws2["A7"] = "分组"
    ws2["B7"] = "数量"
    ws2["A7"].font = ws2["B7"].font = Font(bold=True)
    from collections import Counter
    counts = Counter(g for g, _, _ in ICONS)
    for r, (g, n) in enumerate(counts.items(), 8):
        ws2.cell(row=r, column=1, value=g)
        ws2.cell(row=r, column=2, value=n)
    ws2.column_dimensions["A"].width = 20
    ws2.column_dimensions["B"].width = 50

    OUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_XLSX)
    print(f"Excel 已生成: {OUT_XLSX} ({OUT_XLSX.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
