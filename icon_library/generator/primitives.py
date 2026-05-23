"""
Icon primitive system.

All icons are defined in a 24x24 logical coordinate space (top-left origin, y-down,
matching SVG convention). Each icon is a list of "parts". Each part is a dict
describing one geometric primitive that can be emitted as both SVG and as a
native PowerPoint custGeom freeform shape.

Supported part types:

  - rect:    {"type":"rect","x":,"y":,"w":,"h":,"rx":0}
  - ellipse: {"type":"ellipse","cx":,"cy":,"rx":,"ry":}     (circle = rx==ry)
  - line:    {"type":"line","x1":,"y1":,"x2":,"y2":,"w":}   (rendered as thin filled rect)
  - polygon: {"type":"polygon","points":[(x,y), ...]}
  - path:    {"type":"path","d":"M ... Z"}                  (SVG path subset)
  - donut:   {"type":"donut","cx":,"cy":,"r_outer":,"r_inner":}
  - star:    {"type":"star","cx":,"cy":,"r_outer":,"r_inner":,"points":5,"rot":0}
  - gear:    {"type":"gear","cx":,"cy":,"r_outer":,"r_inner":,"hole_r":,"teeth":8}
  - arrow:   {"type":"arrow","x1":,"y1":,"x2":,"y2":,"shaft_w":,"head_w":,"head_l":}

Every icon is monochrome single-fill, so when the user clicks the group in
PowerPoint and chooses Shape Fill, the entire icon recolors at once.
"""

from __future__ import annotations
import math
from typing import Iterable, Sequence


# ----- helpers ----------------------------------------------------------

def _ang(deg: float) -> float:
    return deg * math.pi / 180.0


def _polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    a = _ang(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def line_to_rect(x1: float, y1: float, x2: float, y2: float, w: float) -> list[tuple[float, float]]:
    """Convert a thick line into a 4-point rotated rectangle polygon."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length      # unit normal
    hw = w / 2.0
    return [
        (x1 + nx * hw, y1 + ny * hw),
        (x2 + nx * hw, y2 + ny * hw),
        (x2 - nx * hw, y2 - ny * hw),
        (x1 - nx * hw, y1 - ny * hw),
    ]


def star_points(cx: float, cy: float, r_outer: float, r_inner: float,
                points: int = 5, rot: float = -90.0) -> list[tuple[float, float]]:
    """Return polygon vertices for an N-point star."""
    out = []
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        deg = rot + i * (180.0 / points)
        out.append(_polar(cx, cy, r, deg))
    return out


def regular_polygon(cx: float, cy: float, r: float, sides: int, rot: float = -90.0
                    ) -> list[tuple[float, float]]:
    return [_polar(cx, cy, r, rot + i * (360.0 / sides)) for i in range(sides)]


def gear_path(cx: float, cy: float, r_outer: float, r_inner: float,
              hole_r: float, teeth: int = 8) -> str:
    """Build an SVG path for a gear (outer toothed ring with center hole).

    Uses even-odd / non-zero fill: the inner hole is drawn in reverse winding
    so it 'punches out' under the default OOXML fill rule we set later.
    """
    half_tooth = 360.0 / (teeth * 2)
    pts = []
    for i in range(teeth):
        base = i * (360.0 / teeth)
        a1 = base - half_tooth * 0.55
        a2 = base - half_tooth * 0.35
        a3 = base + half_tooth * 0.35
        a4 = base + half_tooth * 0.55
        pts.append(_polar(cx, cy, r_inner, a1))
        pts.append(_polar(cx, cy, r_outer, a2))
        pts.append(_polar(cx, cy, r_outer, a3))
        pts.append(_polar(cx, cy, r_inner, a4))
    d = "M %.3f %.3f " % pts[0]
    for x, y in pts[1:]:
        d += "L %.3f %.3f " % (x, y)
    d += "Z "
    # punch a hole (reverse direction)
    if hole_r > 0:
        # circle approximated with 4 cubic beziers, reversed winding
        k = 0.55228 * hole_r
        d += f"M {cx + hole_r:.3f} {cy:.3f} "
        d += f"C {cx + hole_r:.3f} {cy - k:.3f} {cx + k:.3f} {cy - hole_r:.3f} {cx:.3f} {cy - hole_r:.3f} "
        d += f"C {cx - k:.3f} {cy - hole_r:.3f} {cx - hole_r:.3f} {cy - k:.3f} {cx - hole_r:.3f} {cy:.3f} "
        d += f"C {cx - hole_r:.3f} {cy + k:.3f} {cx - k:.3f} {cy + hole_r:.3f} {cx:.3f} {cy + hole_r:.3f} "
        d += f"C {cx + k:.3f} {cy + hole_r:.3f} {cx + hole_r:.3f} {cy + k:.3f} {cx + hole_r:.3f} {cy:.3f} Z"
    return d


def arrow_polygon(x1: float, y1: float, x2: float, y2: float,
                  shaft_w: float = 2.0, head_w: float = 6.0, head_l: float = 5.0
                  ) -> list[tuple[float, float]]:
    """Return polygon vertices for an arrow from (x1,y1) to (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    # tip
    tip = (x2, y2)
    # base of head (where shaft meets head)
    bx, by = x2 - ux * head_l, y2 - uy * head_l
    # shaft corners
    sw = shaft_w / 2.0
    hw = head_w / 2.0
    p1 = (x1 + nx * sw, y1 + ny * sw)            # tail-top
    p2 = (bx + nx * sw, by + ny * sw)            # neck-top
    p3 = (bx + nx * hw, by + ny * hw)            # head-flange-top
    p4 = tip                                      # tip
    p5 = (bx - nx * hw, by - ny * hw)            # head-flange-bot
    p6 = (bx - nx * sw, by - ny * sw)            # neck-bot
    p7 = (x1 - nx * sw, y1 - ny * sw)            # tail-bot
    return [p1, p2, p3, p4, p5, p6, p7]


# ----- expansion: turn high-level parts into normalized primitives -----

def _expand(part: dict) -> list[dict]:
    """Lower a high-level part into a list of low-level parts the renderers
    actually understand: rect, ellipse, polygon, path."""
    t = part["type"]

    if t in ("rect", "ellipse", "polygon", "path"):
        return [part]

    if t == "line":
        pts = line_to_rect(part["x1"], part["y1"], part["x2"], part["y2"], part.get("w", 2.0))
        return [{"type": "polygon", "points": pts}]

    if t == "donut":
        cx, cy = part["cx"], part["cy"]
        ro, ri = part["r_outer"], part["r_inner"]
        # Build a path = outer circle CW then inner circle CCW (punch hole).
        k_o = 0.55228 * ro
        k_i = 0.55228 * ri
        d = (
            f"M {cx + ro:.3f} {cy:.3f} "
            f"C {cx + ro:.3f} {cy + k_o:.3f} {cx + k_o:.3f} {cy + ro:.3f} {cx:.3f} {cy + ro:.3f} "
            f"C {cx - k_o:.3f} {cy + ro:.3f} {cx - ro:.3f} {cy + k_o:.3f} {cx - ro:.3f} {cy:.3f} "
            f"C {cx - ro:.3f} {cy - k_o:.3f} {cx - k_o:.3f} {cy - ro:.3f} {cx:.3f} {cy - ro:.3f} "
            f"C {cx + k_o:.3f} {cy - ro:.3f} {cx + ro:.3f} {cy - k_o:.3f} {cx + ro:.3f} {cy:.3f} Z "
            # inner hole, reverse direction
            f"M {cx + ri:.3f} {cy:.3f} "
            f"C {cx + ri:.3f} {cy - k_i:.3f} {cx + k_i:.3f} {cy - ri:.3f} {cx:.3f} {cy - ri:.3f} "
            f"C {cx - k_i:.3f} {cy - ri:.3f} {cx - ri:.3f} {cy - k_i:.3f} {cx - ri:.3f} {cy:.3f} "
            f"C {cx - ri:.3f} {cy + k_i:.3f} {cx - k_i:.3f} {cy + ri:.3f} {cx:.3f} {cy + ri:.3f} "
            f"C {cx + k_i:.3f} {cy + ri:.3f} {cx + ri:.3f} {cy + k_i:.3f} {cx + ri:.3f} {cy:.3f} Z"
        )
        return [{"type": "path", "d": d, "fill_rule": "evenodd"}]

    if t == "star":
        pts = star_points(part["cx"], part["cy"], part["r_outer"], part["r_inner"],
                          part.get("points", 5), part.get("rot", -90.0))
        return [{"type": "polygon", "points": pts}]

    if t == "gear":
        d = gear_path(part["cx"], part["cy"], part["r_outer"], part["r_inner"],
                      part.get("hole_r", 0), part.get("teeth", 8))
        return [{"type": "path", "d": d, "fill_rule": "evenodd"}]

    if t == "arrow":
        pts = arrow_polygon(
            part["x1"], part["y1"], part["x2"], part["y2"],
            part.get("shaft_w", 2.0), part.get("head_w", 6.0), part.get("head_l", 5.0),
        )
        return [{"type": "polygon", "points": pts}]

    raise ValueError(f"unknown part type: {t}")


def normalize(parts: Sequence[dict]) -> list[dict]:
    """Expand a list of high-level parts to low-level rect/ellipse/polygon/path."""
    out: list[dict] = []
    for p in parts:
        out.extend(_expand(p))
    return out


# ----- transforms (translate / scale) used by composers ---------------

def _t_xy(p: dict, dx: float, dy: float) -> dict:
    p = dict(p)
    t = p["type"]
    if t == "rect":
        p["x"] += dx
        p["y"] += dy
    elif t == "ellipse":
        p["cx"] += dx
        p["cy"] += dy
    elif t == "line":
        p["x1"] += dx; p["x2"] += dx
        p["y1"] += dy; p["y2"] += dy
    elif t == "polygon":
        p["points"] = [(x + dx, y + dy) for (x, y) in p["points"]]
    elif t == "path":
        p["d"] = _path_translate(p["d"], dx, dy)
    elif t in ("donut", "star", "gear"):
        p["cx"] += dx; p["cy"] += dy
    elif t == "arrow":
        p["x1"] += dx; p["x2"] += dx
        p["y1"] += dy; p["y2"] += dy
    return p


def _t_scale_about(p: dict, sx: float, sy: float, ax: float, ay: float) -> dict:
    """Scale a part about anchor (ax,ay)."""
    p = dict(p)
    t = p["type"]

    def sxy(x, y):
        return (ax + (x - ax) * sx, ay + (y - ay) * sy)

    if t == "rect":
        x0, y0 = sxy(p["x"], p["y"])
        x1, y1 = sxy(p["x"] + p["w"], p["y"] + p["h"])
        p["x"], p["y"] = x0, y0
        p["w"], p["h"] = x1 - x0, y1 - y0
        if "rx" in p:
            p["rx"] = p["rx"] * (sx + sy) / 2.0
    elif t == "ellipse":
        cx, cy = sxy(p["cx"], p["cy"])
        p["cx"], p["cy"] = cx, cy
        p["rx"] = p["rx"] * sx
        p["ry"] = p["ry"] * sy
    elif t == "line":
        x1, y1 = sxy(p["x1"], p["y1"])
        x2, y2 = sxy(p["x2"], p["y2"])
        p["x1"], p["y1"] = x1, y1
        p["x2"], p["y2"] = x2, y2
        p["w"] = p.get("w", 2.0) * (sx + sy) / 2.0
    elif t == "polygon":
        p["points"] = [sxy(x, y) for (x, y) in p["points"]]
    elif t == "path":
        p["d"] = _path_scale_about(p["d"], sx, sy, ax, ay)
    elif t == "donut":
        cx, cy = sxy(p["cx"], p["cy"])
        p["cx"], p["cy"] = cx, cy
        avg = (sx + sy) / 2.0
        p["r_outer"] *= avg
        p["r_inner"] *= avg
    elif t == "star":
        cx, cy = sxy(p["cx"], p["cy"])
        p["cx"], p["cy"] = cx, cy
        avg = (sx + sy) / 2.0
        p["r_outer"] *= avg
        p["r_inner"] *= avg
    elif t == "gear":
        cx, cy = sxy(p["cx"], p["cy"])
        p["cx"], p["cy"] = cx, cy
        avg = (sx + sy) / 2.0
        p["r_outer"] *= avg
        p["r_inner"] *= avg
        p["hole_r"] = p.get("hole_r", 0) * avg
    elif t == "arrow":
        x1, y1 = sxy(p["x1"], p["y1"])
        x2, y2 = sxy(p["x2"], p["y2"])
        p["x1"], p["y1"] = x1, y1
        p["x2"], p["y2"] = x2, y2
        avg = (sx + sy) / 2.0
        for k in ("shaft_w", "head_w", "head_l"):
            if k in p:
                p[k] *= avg
    return p


def translate(parts: Iterable[dict], dx: float, dy: float) -> list[dict]:
    return [_t_xy(p, dx, dy) for p in parts]


def scale_about(parts: Iterable[dict], sx: float, sy: float,
                ax: float = 12.0, ay: float = 12.0) -> list[dict]:
    return [_t_scale_about(p, sx, sy, ax, ay) for p in parts]


def fit(parts: Iterable[dict], box: tuple[float, float, float, float],
        src_box: tuple[float, float, float, float] = (0, 0, 24, 24)) -> list[dict]:
    """Place a sub-icon (defined in src_box) into target box (x,y,w,h)."""
    sx0, sy0, sw, sh = src_box
    tx, ty, tw, th = box
    s_x = tw / sw
    s_y = th / sh
    out = []
    for p in parts:
        # translate so src origin -> 0
        p2 = _t_xy(p, -sx0, -sy0)
        # scale about origin
        p2 = _t_scale_about(p2, s_x, s_y, 0, 0)
        # translate to target origin
        p2 = _t_xy(p2, tx, ty)
        out.append(p2)
    return out


# ----- minimal SVG path translate / scale -----

def _tokenize_path(d: str) -> list[str]:
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


def _path_translate(d: str, dx: float, dy: float) -> str:
    return _path_transform(d, lambda x, y: (x + dx, y + dy))


def _path_scale_about(d: str, sx: float, sy: float, ax: float, ay: float) -> str:
    return _path_transform(d, lambda x, y: (ax + (x - ax) * sx, ay + (y - ay) * sy))


def _path_transform(d: str, fn) -> str:
    toks = _tokenize_path(d)
    out: list[str] = []
    i = 0
    while i < len(toks):
        cmd = toks[i]
        if cmd in ("M", "L", "T"):
            x = float(toks[i + 1]); y = float(toks[i + 2])
            x, y = fn(x, y)
            out.extend([cmd, f"{x:.3f}", f"{y:.3f}"])
            i += 3
        elif cmd in ("C",):
            xs = list(map(float, toks[i + 1:i + 7]))
            (x1, y1), (x2, y2), (x3, y3) = (
                fn(xs[0], xs[1]), fn(xs[2], xs[3]), fn(xs[4], xs[5])
            )
            out.extend([cmd,
                        f"{x1:.3f}", f"{y1:.3f}",
                        f"{x2:.3f}", f"{y2:.3f}",
                        f"{x3:.3f}", f"{y3:.3f}"])
            i += 7
        elif cmd in ("Q", "S"):
            xs = list(map(float, toks[i + 1:i + 5]))
            (x1, y1), (x2, y2) = fn(xs[0], xs[1]), fn(xs[2], xs[3])
            out.extend([cmd, f"{x1:.3f}", f"{y1:.3f}", f"{x2:.3f}", f"{y2:.3f}"])
            i += 5
        elif cmd == "Z":
            out.append(cmd)
            i += 1
        else:
            # unsupported — just pass through token unchanged
            out.append(cmd)
            i += 1
    return " ".join(out)
