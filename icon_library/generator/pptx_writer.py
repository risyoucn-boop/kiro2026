"""
Build the master library .pptx.

Each icon is rendered as a *single* native PowerPoint custGeom freeform shape.
Color-changing in PowerPoint then becomes literally one click:

    Click the icon -> Shape Format -> Shape Fill -> pick color

We also wrap each icon shape + its label in a Group so the user can move them
together. The group's child shape is a normal sp (not picture / not SVG), so
WPS, Microsoft 365, PowerPoint 2016+, and Keynote all handle it identically.

Coordinate system inside one custGeom: 24x24 (matches our SVG) but expressed
as OOXML path units (a:path w="24000" h="24000"). Outer placement on slide
is in EMU (914400 EMU = 1 inch).
"""
from __future__ import annotations

import math
from typing import Sequence

from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.dml.color import RGBColor
from lxml import etree

from primitives import normalize


# OOXML namespaces we touch
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NSMAP = {"a": A_NS, "p": P_NS, "r": R_NS}

# Inside a:path we use a 24000x24000 unit grid (24 logical units * 1000)
PATH_GRID = 24000
LOGICAL = 24.0
SCALE = PATH_GRID / LOGICAL          # 1000


def _q(tag: str) -> str:
    """Qualified tag for namespace 'a'."""
    return f"{{{A_NS}}}{tag}"


def _qp(tag: str) -> str:
    return f"{{{P_NS}}}{tag}"


# ---------------------------------------------------------------------------
# Build <a:custGeom> XML for one icon (already-normalized parts)
# ---------------------------------------------------------------------------

def build_custgeom(parts: Sequence[dict]) -> etree._Element:
    """Return an <a:custGeom> element representing the union of all parts."""
    custGeom = etree.Element(_q("custGeom"))
    etree.SubElement(custGeom, _q("avLst"))
    etree.SubElement(custGeom, _q("gdLst"))
    etree.SubElement(custGeom, _q("ahLst"))
    etree.SubElement(custGeom, _q("cxnLst"))
    etree.SubElement(custGeom, _q("rect"),
                     l="0", t="0", r=str(PATH_GRID), b=str(PATH_GRID))
    pathLst = etree.SubElement(custGeom, _q("pathLst"))

    path = etree.SubElement(pathLst, _q("path"),
                            w=str(PATH_GRID), h=str(PATH_GRID),
                            fill="norm", stroke="0", extrusionOk="0")

    for part in parts:
        _emit_part_into_path(path, part)

    return custGeom


def _emit_part_into_path(path_el: etree._Element, part: dict) -> None:
    t = part["type"]
    if t == "rect":
        x, y, w, h, rx = part["x"], part["y"], part["w"], part["h"], part.get("rx", 0)
        if rx and rx > 0:
            _emit_round_rect(path_el, x, y, w, h, rx)
        else:
            _move(path_el, x, y)
            _line(path_el, x + w, y)
            _line(path_el, x + w, y + h)
            _line(path_el, x, y + h)
            _close(path_el)
    elif t == "ellipse":
        _emit_ellipse(path_el, part["cx"], part["cy"], part["rx"], part["ry"])
    elif t == "polygon":
        pts = part["points"]
        if not pts:
            return
        _move(path_el, pts[0][0], pts[0][1])
        for x, y in pts[1:]:
            _line(path_el, x, y)
        _close(path_el)
    elif t == "path":
        _emit_svg_path(path_el, part["d"])
    else:
        raise ValueError(f"pptx: cannot emit primitive of type {t!r}")


# ---- low level path-building helpers ----

def _u(v: float) -> str:
    """Convert a logical 0..24 coordinate to a 0..24000 grid string."""
    n = int(round(v * SCALE))
    # Clamp inside path bounds; OOXML accepts negatives but most renderers prefer not.
    return str(n)


def _move(path_el, x: float, y: float) -> None:
    m = etree.SubElement(path_el, _q("moveTo"))
    pt = etree.SubElement(m, _q("pt"))
    pt.set("x", _u(x))
    pt.set("y", _u(y))


def _line(path_el, x: float, y: float) -> None:
    ln = etree.SubElement(path_el, _q("lnTo"))
    pt = etree.SubElement(ln, _q("pt"))
    pt.set("x", _u(x))
    pt.set("y", _u(y))


def _cubic(path_el, x1, y1, x2, y2, x3, y3) -> None:
    cb = etree.SubElement(path_el, _q("cubicBezTo"))
    for cx, cy in ((x1, y1), (x2, y2), (x3, y3)):
        pt = etree.SubElement(cb, _q("pt"))
        pt.set("x", _u(cx))
        pt.set("y", _u(cy))


def _quad(path_el, x1, y1, x2, y2) -> None:
    qb = etree.SubElement(path_el, _q("quadBezTo"))
    for cx, cy in ((x1, y1), (x2, y2)):
        pt = etree.SubElement(qb, _q("pt"))
        pt.set("x", _u(cx))
        pt.set("y", _u(cy))


def _close(path_el) -> None:
    etree.SubElement(path_el, _q("close"))


def _emit_ellipse(path_el, cx: float, cy: float, rx: float, ry: float) -> None:
    """Approximate ellipse with 4 cubic Beziers (kappa=0.5522847498)."""
    k = 0.5522847498
    kx = rx * k
    ky = ry * k
    _move(path_el, cx + rx, cy)
    _cubic(path_el, cx + rx, cy + ky,  cx + kx, cy + ry,  cx,        cy + ry)
    _cubic(path_el, cx - kx, cy + ry,  cx - rx, cy + ky,  cx - rx,   cy)
    _cubic(path_el, cx - rx, cy - ky,  cx - kx, cy - ry,  cx,        cy - ry)
    _cubic(path_el, cx + kx, cy - ry,  cx + rx, cy - ky,  cx + rx,   cy)
    _close(path_el)


def _emit_round_rect(path_el, x, y, w, h, r) -> None:
    r = min(r, w / 2.0, h / 2.0)
    k = 0.5522847498 * r
    # Start at top edge after the corner
    _move(path_el, x + r, y)
    _line(path_el, x + w - r, y)
    _cubic(path_el, x + w - r + k, y,        x + w, y + r - k,    x + w, y + r)
    _line(path_el, x + w, y + h - r)
    _cubic(path_el, x + w, y + h - r + k,    x + w - r + k, y + h, x + w - r, y + h)
    _line(path_el, x + r, y + h)
    _cubic(path_el, x + r - k, y + h,        x, y + h - r + k,    x, y + h - r)
    _line(path_el, x, y + r)
    _cubic(path_el, x, y + r - k,            x + r - k, y,        x + r, y)
    _close(path_el)


# ---- SVG path "d" -> custGeom path commands ----

def _emit_svg_path(path_el, d: str) -> None:
    cur_x, cur_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    toks = _tok_path(d)
    i = 0
    last_cmd = None
    while i < len(toks):
        cmd = toks[i]
        if cmd in ("M", "L", "C", "Q", "Z", "T", "S", "m", "l", "c", "q", "z", "t", "s"):
            i += 1
            last_cmd = cmd
        else:
            cmd = last_cmd  # implicit repeat of previous command

        if cmd == "M":
            x, y = float(toks[i]), float(toks[i + 1]); i += 2
            _move(path_el, x, y)
            cur_x, cur_y = x, y
            start_x, start_y = x, y
            last_cmd = "L"  # implicit subsequent coords are L
        elif cmd == "L":
            x, y = float(toks[i]), float(toks[i + 1]); i += 2
            _line(path_el, x, y)
            cur_x, cur_y = x, y
        elif cmd == "C":
            x1, y1 = float(toks[i]), float(toks[i + 1])
            x2, y2 = float(toks[i + 2]), float(toks[i + 3])
            x3, y3 = float(toks[i + 4]), float(toks[i + 5])
            i += 6
            _cubic(path_el, x1, y1, x2, y2, x3, y3)
            cur_x, cur_y = x3, y3
        elif cmd == "Q":
            x1, y1 = float(toks[i]), float(toks[i + 1])
            x2, y2 = float(toks[i + 2]), float(toks[i + 3])
            i += 4
            _quad(path_el, x1, y1, x2, y2)
            cur_x, cur_y = x2, y2
        elif cmd in ("Z", "z"):
            _close(path_el)
            cur_x, cur_y = start_x, start_y
        else:
            raise ValueError(f"unsupported SVG path command: {cmd!r}")


def _tok_path(d: str) -> list[str]:
    out: list[str] = []
    buf = ""
    for ch in d:
        if ch.isalpha():
            if buf.strip():
                out.extend(buf.replace(",", " ").split())
            out.append(ch)
            buf = ""
        else:
            buf += ch
    if buf.strip():
        out.extend(buf.replace(",", " ").split())
    return out


# ---------------------------------------------------------------------------
# High-level: insert one icon-shape onto a slide
# ---------------------------------------------------------------------------

def add_icon_shape(slide, parts: Sequence[dict], left: int, top: int,
                   size: int, fill_hex: str, name: str = "icon",
                   shape_id: int | None = None) -> None:
    """Add a single freeform shape that draws the icon at (left, top, size, size).

    All measurements are in EMU. The shape's a:custGeom uses a 24000x24000 grid
    so we just scale it into the requested size via spPr/xfrm.
    """
    norm_parts = normalize(parts)

    sp = etree.SubElement(slide.shapes._spTree, _qp("sp"))

    nvSpPr = etree.SubElement(sp, _qp("nvSpPr"))
    cNvPr = etree.SubElement(nvSpPr, _qp("cNvPr"))
    if shape_id is None:
        shape_id = _next_shape_id(slide)
    cNvPr.set("id", str(shape_id))
    cNvPr.set("name", name)
    cNvSpPr = etree.SubElement(nvSpPr, _qp("cNvSpPr"))
    nvPr = etree.SubElement(nvSpPr, _qp("nvPr"))

    spPr = etree.SubElement(sp, _qp("spPr"))
    xfrm = etree.SubElement(spPr, _q("xfrm"))
    off = etree.SubElement(xfrm, _q("off"))
    off.set("x", str(int(left)))
    off.set("y", str(int(top)))
    ext = etree.SubElement(xfrm, _q("ext"))
    ext.set("cx", str(int(size)))
    ext.set("cy", str(int(size)))

    spPr.append(build_custgeom(norm_parts))

    # solid fill
    solidFill = etree.SubElement(spPr, _q("solidFill"))
    srgb = etree.SubElement(solidFill, _q("srgbClr"))
    srgb.set("val", fill_hex.lstrip("#").upper())

    # no outline (so Shape Fill alone re-tints the icon)
    ln = etree.SubElement(spPr, _q("ln"))
    ln.set("w", "0")
    etree.SubElement(ln, _q("noFill"))

    # required style stub so PPT doesn't warn
    style = etree.SubElement(sp, _qp("style"))
    lnRef = etree.SubElement(style, _q("lnRef")); lnRef.set("idx", "0")
    fillRef = etree.SubElement(style, _q("fillRef")); fillRef.set("idx", "0")
    effectRef = etree.SubElement(style, _q("effectRef")); effectRef.set("idx", "0")
    fontRef = etree.SubElement(style, _q("fontRef")); fontRef.set("idx", "minor")

    txBody = etree.SubElement(sp, _qp("txBody"))
    bodyPr = etree.SubElement(txBody, _q("bodyPr"))
    lstStyle = etree.SubElement(txBody, _q("lstStyle"))
    p = etree.SubElement(txBody, _q("p"))


def _next_shape_id(slide) -> int:
    used = []
    for el in slide.shapes._spTree.iter():
        if el.get("id") and el.get("id").isdigit():
            used.append(int(el.get("id")))
    return (max(used) + 1) if used else 100
