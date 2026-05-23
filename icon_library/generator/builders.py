"""Shape-builder helpers used everywhere in the icon catalog.

These are tiny convenience wrappers that produce the 'part dicts' understood
by primitives.normalize(). They keep icon definitions short and readable.
"""
from __future__ import annotations
import math
from typing import Iterable

from primitives import normalize, translate, scale_about, fit, line_to_rect, star_points, regular_polygon


def rect(x, y, w, h, rx=0):
    return {"type": "rect", "x": x, "y": y, "w": w, "h": h, "rx": rx}


def circle(cx, cy, r):
    return {"type": "ellipse", "cx": cx, "cy": cy, "rx": r, "ry": r}


def ellipse(cx, cy, rx, ry):
    return {"type": "ellipse", "cx": cx, "cy": cy, "rx": rx, "ry": ry}


def line(x1, y1, x2, y2, w=2.0):
    return {"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "w": w}


def polygon(points):
    return {"type": "polygon", "points": list(points)}


def path(d, fill_rule="nonzero"):
    return {"type": "path", "d": d, "fill_rule": fill_rule}


def donut(cx, cy, r_outer, r_inner):
    return {"type": "donut", "cx": cx, "cy": cy, "r_outer": r_outer, "r_inner": r_inner}


def star(cx, cy, r_outer, r_inner, points=5, rot=-90.0):
    return {"type": "star", "cx": cx, "cy": cy, "r_outer": r_outer, "r_inner": r_inner,
            "points": points, "rot": rot}


def gear(cx, cy, r_outer=10, r_inner=7.5, hole_r=3, teeth=8):
    return {"type": "gear", "cx": cx, "cy": cy, "r_outer": r_outer, "r_inner": r_inner,
            "hole_r": hole_r, "teeth": teeth}


def arrow(x1, y1, x2, y2, shaft_w=2.4, head_w=6.5, head_l=5.5):
    return {"type": "arrow", "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "shaft_w": shaft_w, "head_w": head_w, "head_l": head_l}


# --- composite helpers ---

def round_rect(x, y, w, h, r):
    return rect(x, y, w, h, rx=r)


def square_centered(cx, cy, side, rx=0):
    return rect(cx - side/2, cy - side/2, side, side, rx=rx)


def triangle(p1, p2, p3):
    return polygon([p1, p2, p3])


def diamond(cx, cy, r):
    return polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)])


def hex_h(cx, cy, r):
    """Horizontal hexagon (pointy left/right)."""
    return polygon(regular_polygon(cx, cy, r, 6, rot=0))


def hex_v(cx, cy, r):
    """Vertical hexagon (pointy top/bottom)."""
    return polygon(regular_polygon(cx, cy, r, 6, rot=-90))


def cross_x(cx, cy, size, w=2.4):
    """An X cross shape."""
    h = size / 2
    return [
        line(cx - h, cy - h, cx + h, cy + h, w=w),
        line(cx - h, cy + h, cx + h, cy - h, w=w),
    ]


def plus_cross(cx, cy, size, w=2.4):
    h = size / 2
    return [
        line(cx - h, cy, cx + h, cy, w=w),
        line(cx, cy - h, cx, cy + h, w=w),
    ]


def check_mark(cx, cy, size=8.0, w=2.4):
    """A V-shaped checkmark centered at (cx,cy)."""
    s = size / 2
    return [
        line(cx - s * 0.9, cy + s * 0.05, cx - s * 0.2, cy + s * 0.7, w=w),
        line(cx - s * 0.2, cy + s * 0.7, cx + s * 0.95, cy - s * 0.55, w=w),
    ]


def cross_xs(cx, cy, size=8.0, w=2.2):
    return cross_x(cx, cy, size, w=w)


def small_arrow_up(cx, cy, size=4.0, w=1.6):
    s = size / 2
    return [arrow(cx, cy + s, cx, cy - s, shaft_w=w, head_w=size * 0.9, head_l=size * 0.7)]


def small_arrow_down(cx, cy, size=4.0, w=1.6):
    s = size / 2
    return [arrow(cx, cy - s, cx, cy + s, shaft_w=w, head_w=size * 0.9, head_l=size * 0.7)]


def small_arrow_right(cx, cy, size=4.0, w=1.6):
    s = size / 2
    return [arrow(cx - s, cy, cx + s, cy, shaft_w=w, head_w=size * 0.9, head_l=size * 0.7)]


def small_arrow_left(cx, cy, size=4.0, w=1.6):
    s = size / 2
    return [arrow(cx + s, cy, cx - s, cy, shaft_w=w, head_w=size * 0.9, head_l=size * 0.7)]


def exclam(cx, cy, h=8, w=1.6):
    """Exclamation mark centered."""
    top = cy - h / 2 + 0.5
    return [
        rect(cx - w / 2, top, w, h * 0.65, rx=w * 0.3),
        circle(cx, cy + h / 2 - 0.6, w * 0.55),
    ]


def question(cx, cy, h=8):
    """Question mark using a small arc + dot."""
    # approximate ? with a path
    s = h / 8.0
    d = (
        f"M {cx - 2*s:.2f} {cy - 3.2*s:.2f} "
        f"C {cx - 2*s:.2f} {cy - 4.5*s:.2f} {cx + 2*s:.2f} {cy - 4.5*s:.2f} {cx + 2*s:.2f} {cy - 2.8*s:.2f} "
        f"C {cx + 2*s:.2f} {cy - 1.4*s:.2f} {cx + 0.4*s:.2f} {cy - 1*s:.2f} {cx + 0.4*s:.2f} {cy + 0.6*s:.2f} "
        f"L {cx - 0.6*s:.2f} {cy + 0.6*s:.2f} "
        f"C {cx - 0.6*s:.2f} {cy - 1.6*s:.2f} {cx + 1.0*s:.2f} {cy - 1.8*s:.2f} {cx + 1.0*s:.2f} {cy - 2.8*s:.2f} "
        f"C {cx + 1.0*s:.2f} {cy - 3.4*s:.2f} {cx - 1*s:.2f} {cy - 3.4*s:.2f} {cx - 1*s:.2f} {cy - 3.2*s:.2f} Z"
    )
    return [path(d), circle(cx - 0.05 * s, cy + 2.4 * s, 0.7 * s)]


# --- complex glyph parts (used as building blocks for many icons) ---

def doc_outline(x=4, y=2, w=15, h=20, fold=4):
    """Document silhouette with folded corner: solid filled outline form using a path."""
    d = (
        f"M {x} {y} "
        f"L {x + w - fold} {y} "
        f"L {x + w} {y + fold} "
        f"L {x + w} {y + h} "
        f"L {x} {y + h} Z "
        # punched-out fold (reverse winding)
        f"M {x + w - fold} {y} "
        f"L {x + w - fold} {y + fold} "
        f"L {x + w} {y + fold} "
        f"L {x + w - fold} {y} Z"
    )
    return [path(d, fill_rule="evenodd")]


def folder_outline(x=2, y=6, w=20, h=14, tab_w=8, tab_h=2.5):
    d = (
        f"M {x} {y + tab_h} "
        f"L {x} {y} "
        f"L {x + tab_w} {y} "
        f"L {x + tab_w + 1.5} {y + tab_h} "
        f"L {x + w} {y + tab_h} "
        f"L {x + w} {y + h} "
        f"L {x} {y + h} Z"
    )
    return [path(d)]


def shield_outline(cx=12, top=2, w=18, h=20):
    """Solid shield silhouette."""
    half = w / 2
    bottom = top + h
    d = (
        f"M {cx} {top} "
        f"L {cx + half} {top + 3} "
        f"L {cx + half} {top + h * 0.55} "
        f"C {cx + half} {bottom - 1} {cx + half * 0.6} {bottom} {cx} {bottom} "
        f"C {cx - half * 0.6} {bottom} {cx - half} {bottom - 1} {cx - half} {top + h * 0.55} "
        f"L {cx - half} {top + 3} Z"
    )
    return [path(d)]


def chevron_right(cx, cy, w=4, h=8, t=2):
    """Right-pointing chevron arrow as a thick filled '>'."""
    pts = [
        (cx - w/2, cy - h/2),
        (cx + w/2 - t, cy - h/2),
        (cx + w/2, cy),
        (cx + w/2 - t, cy + h/2),
        (cx - w/2, cy + h/2),
        (cx - w/2 + t, cy),
    ]
    return [polygon(pts)]


def speech_bubble(x=2, y=3, w=20, h=14, tail_x=8, r=2.5):
    """Speech bubble with tail at the bottom-left."""
    rb = y + h
    d = (
        f"M {x + r} {y} "
        f"L {x + w - r} {y} "
        f"Q {x + w} {y} {x + w} {y + r} "
        f"L {x + w} {rb - r} "
        f"Q {x + w} {rb} {x + w - r} {rb} "
        f"L {tail_x + 2.4} {rb} "
        f"L {tail_x - 1} {rb + 3} "
        f"L {tail_x} {rb} "
        f"L {x + r} {rb} "
        f"Q {x} {rb} {x} {rb - r} "
        f"L {x} {y + r} "
        f"Q {x} {y} {x + r} {y} Z"
    )
    return [path(d)]


def cloud_outline(cx=12, cy=14, w=18, h=10):
    """Cloud silhouette built from overlapping circles + base."""
    # simplified: 4 bumps
    parts = [
        circle(cx - 5, cy - 1, 4.5),
        circle(cx, cy - 3, 5.5),
        circle(cx + 5, cy - 1, 4.5),
        circle(cx + 2, cy + 1, 4.0),
        rect(cx - 7, cy + 0.5, 14, 4, rx=2),
    ]
    return parts


def heart_path(cx=12, cy=12, w=18, h=16):
    """Solid heart silhouette."""
    half = w / 2
    top = cy - h / 2
    d = (
        f"M {cx} {cy + h / 2} "
        f"C {cx - half * 1.1} {cy + h * 0.15} {cx - half} {top + h * 0.05} {cx - half * 0.55} {top + h * 0.05} "
        f"C {cx - half * 0.2} {top + h * 0.05} {cx} {top + h * 0.25} {cx} {top + h * 0.4} "
        f"C {cx} {top + h * 0.25} {cx + half * 0.2} {top + h * 0.05} {cx + half * 0.55} {top + h * 0.05} "
        f"C {cx + half} {top + h * 0.05} {cx + half * 1.1} {cy + h * 0.15} {cx} {cy + h / 2} Z"
    )
    return [path(d)]


def person_glyph(cx=12, head_cy=7, head_r=3.2, body_top=10, body_w=11, body_h=11, body_r=3.5):
    return [
        circle(cx, head_cy, head_r),
        path(
            f"M {cx - body_w/2} {body_top + body_h} "
            f"L {cx - body_w/2} {body_top + body_r} "
            f"C {cx - body_w/2} {body_top} {cx + body_w/2} {body_top} {cx + body_w/2} {body_top + body_r} "
            f"L {cx + body_w/2} {body_top + body_h} Z"
        ),
    ]


def magnifier(cx=10, cy=10, r=5.5, handle_to=(20, 20), handle_w=2.2):
    """Magnifying glass."""
    inner = r * 0.6
    parts = [donut(cx, cy, r, inner)]
    # handle from (cx + r * cos45, cy + r * sin45) to handle_to
    a = math.pi / 4
    sx = cx + r * math.cos(a)
    sy = cy + r * math.sin(a)
    parts.append(line(sx, sy, handle_to[0], handle_to[1], w=handle_w))
    return parts


def clock_glyph(cx=12, cy=12, r=8.5):
    """Clock with hour and minute hand at ~10:10."""
    return [
        donut(cx, cy, r, r - 1.6),
        line(cx, cy, cx + r * 0.45, cy - r * 0.45, w=1.4),  # minute hand
        line(cx, cy, cx - r * 0.5, cy - r * 0.05, w=1.4),  # hour hand
        circle(cx, cy, 1.0),
    ]


def bullseye(cx=12, cy=12, r_outer=10):
    """Concentric ring + dot center."""
    return [
        donut(cx, cy, r_outer, r_outer - 2),
        donut(cx, cy, r_outer - 4, r_outer - 5.6),
        circle(cx, cy, 1.4),
    ]


def gauge_glyph(cx=12, cy=14, r=9):
    """Speedometer / gauge."""
    # outer arc
    d = (
        f"M {cx - r} {cy} "
        f"A {r} {r} 0 0 1 {cx + r} {cy} "
        f"L {cx + r - 1.6} {cy} "
        f"A {r - 1.6} {r - 1.6} 0 0 0 {cx - r + 1.6} {cy} Z"
    )
    # we don't support A in our path engine; instead approximate arc with two cubic beziers
    return [
        # half-donut top
        path(_half_donut_path(cx, cy, r, r - 1.6, top=True)),
        # needle
        line(cx, cy, cx + r * 0.5, cy - r * 0.55, w=1.4),
        circle(cx, cy, 1.4),
    ]


def _half_donut_path(cx, cy, ro, ri, top=True) -> str:
    """Half donut (180 deg). top=True -> upper half."""
    k_o = 0.5522847498 * ro
    k_i = 0.5522847498 * ri
    if top:
        return (
            f"M {cx - ro} {cy} "
            f"C {cx - ro} {cy - k_o} {cx - k_o} {cy - ro} {cx} {cy - ro} "
            f"C {cx + k_o} {cy - ro} {cx + ro} {cy - k_o} {cx + ro} {cy} "
            f"L {cx + ri} {cy} "
            f"C {cx + ri} {cy - k_i} {cx + k_i} {cy - ri} {cx} {cy - ri} "
            f"C {cx - k_i} {cy - ri} {cx - ri} {cy - k_i} {cx - ri} {cy} Z"
        )
    else:
        return (
            f"M {cx + ro} {cy} "
            f"C {cx + ro} {cy + k_o} {cx + k_o} {cy + ro} {cx} {cy + ro} "
            f"C {cx - k_o} {cy + ro} {cx - ro} {cy + k_o} {cx - ro} {cy} "
            f"L {cx - ri} {cy} "
            f"C {cx - ri} {cy + k_i} {cx - k_i} {cy + ri} {cx} {cy + ri} "
            f"C {cx + k_i} {cy + ri} {cx + ri} {cy + k_i} {cx + ri} {cy} Z"
        )


def lightbulb_glyph(cx=12, cy=10, r=5):
    return [
        circle(cx, cy, r),
        rect(cx - 2.5, cy + r - 0.5, 5, 1.5, rx=0.4),
        rect(cx - 2.0, cy + r + 1.5, 4, 1.2, rx=0.4),
        rect(cx - 1.4, cy + r + 3.2, 2.8, 1.0, rx=0.4),
    ]


def flag_glyph(x=4, top=2, h=20, flag_w=12, flag_h=8):
    return [
        rect(x, top, 1.6, h, rx=0.3),
        path(
            f"M {x + 1.6} {top + 0.5} "
            f"L {x + 1.6 + flag_w} {top + 0.5} "
            f"L {x + 1.6 + flag_w * 0.78} {top + 0.5 + flag_h * 0.5} "
            f"L {x + 1.6 + flag_w} {top + 0.5 + flag_h} "
            f"L {x + 1.6} {top + 0.5 + flag_h} Z"
        ),
    ]


def lock_glyph(cx=12, cy=14, w=12, h=10, hasp_h=5):
    body = round_rect(cx - w/2, cy - h/2, w, h, r=1.5)
    hasp = path(
        f"M {cx - 3.5} {cy - h/2} "
        f"L {cx - 3.5} {cy - h/2 - hasp_h + 1.5} "
        f"C {cx - 3.5} {cy - h/2 - hasp_h - 1.5} {cx + 3.5} {cy - h/2 - hasp_h - 1.5} {cx + 3.5} {cy - h/2 - hasp_h + 1.5} "
        f"L {cx + 3.5} {cy - h/2} "
        f"L {cx + 1.8} {cy - h/2} "
        f"L {cx + 1.8} {cy - h/2 - hasp_h + 1.6} "
        f"C {cx + 1.8} {cy - h/2 - hasp_h - 0.2} {cx - 1.8} {cy - h/2 - hasp_h - 0.2} {cx - 1.8} {cy - h/2 - hasp_h + 1.6} "
        f"L {cx - 1.8} {cy - h/2} Z"
    )
    return [body, hasp]


def key_glyph(cx=8, cy=12, ring_r=4, length=12):
    return [
        donut(cx, cy, ring_r, ring_r - 1.6),
        rect(cx + ring_r - 0.5, cy - 0.8, length - ring_r + 0.5, 1.6),
        rect(cx + length - 4, cy + 0.2, 1.2, 2.5),
        rect(cx + length - 1.6, cy + 0.2, 1.2, 2.5),
    ]


def envelope_glyph(x=2, y=5, w=20, h=14):
    return [
        round_rect(x, y, w, h, r=1.4),
        path(
            f"M {x} {y + 1.0} "
            f"L {x + w/2} {y + h * 0.55} "
            f"L {x + w} {y + 1.0} "
            f"L {x + w} {y + 0.0} "
            f"L {x} {y + 0.0} Z",
            fill_rule="evenodd"
        ),
    ]


def chat_bubble_pair():
    return [
        path(
            "M 2 5 L 14 5 Q 16 5 16 7 L 16 13 Q 16 15 14 15 L 8 15 L 5 18 L 5 15 L 4 15 Q 2 15 2 13 Z"
        ),
        path(
            "M 9 9 L 21 9 Q 22.5 9 22.5 10.5 L 22.5 16 Q 22.5 17.5 21 17.5 L 19 17.5 L 19 20 L 16 17.5 L 11 17.5 Q 9 17.5 9 16 L 9 11 Q 9 9 11 9 Z",
            fill_rule="evenodd"
        ),
    ]


def phone_glyph():
    return [path(
        "M 5 3 "
        "L 9 3 "
        "L 11 8 "
        "L 8.5 10 "
        "C 9.5 13 11 14.5 14 15.5 "
        "L 16 13 "
        "L 21 15 "
        "L 21 19 "
        "C 21 20.5 20 21 18.5 21 "
        "C 11 21 3 13 3 5.5 "
        "C 3 4 3.5 3 5 3 Z"
    )]


def chart_bars(heights=(6, 11, 16), x_start=4, baseline=20, bar_w=3, gap=2):
    parts = [rect(2, baseline, 20, 1.2, rx=0.3)]
    x = x_start
    for h in heights:
        parts.append(rect(x, baseline - h, bar_w, h, rx=0.3))
        x += bar_w + gap
    return parts


def chart_line(points, baseline=20, with_axis=True):
    parts = []
    if with_axis:
        parts.append(rect(2, baseline, 20, 1.0, rx=0.2))
        parts.append(rect(2, 3, 1.0, baseline - 2, rx=0.2))
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        parts.append(line(x1, y1, x2, y2, w=1.6))
    for x, y in points:
        parts.append(circle(x, y, 1.0))
    return parts


def chart_pie(slice_deg=90, cx=12, cy=12, r=9):
    """Pie ring with one highlighted slice (the wedge is a separate shape)."""
    parts = [donut(cx, cy, r, r - 0.1)]  # ring outline
    # main filled disk minus inverted wedge: simpler — full disk
    parts = [circle(cx, cy, r)]
    # punch a wedge missing for slice_deg using a polygon mask is hard,
    # so we just draw a contrasting wedge as another shape that, since it's
    # the same color, just makes the icon a full pie. The "split" effect
    # comes from showing radial lines:
    parts.append(line(cx, cy, cx + r, cy, w=1.0))
    parts.append(line(cx, cy, cx, cy - r, w=1.0))
    return parts


def database_cylinder(cx=12, cy_top=4, w=14, h=16):
    rx = w / 2
    ry = 2.0
    parts = [
        ellipse(cx, cy_top, rx, ry),
        rect(cx - rx, cy_top, w, h, rx=0),
        ellipse(cx, cy_top + h, rx, ry),
        ellipse(cx, cy_top + h * 0.33, rx, ry),
        ellipse(cx, cy_top + h * 0.66, rx, ry),
    ]
    return parts


def factory_glyph():
    """Simple factory silhouette."""
    return [
        path(
            "M 3 21 L 3 11 L 9 13 L 9 11 L 15 13 L 15 11 L 21 14 L 21 21 Z"
        ),
        rect(5, 2, 3, 11, rx=0.5),
        rect(5, 1, 3, 1.5, rx=0.4),
    ]


def server_rack(cx=12):
    return [
        round_rect(3, 4, 18, 6, 1.2),
        round_rect(3, 14, 18, 6, 1.2),
        circle(6, 7, 0.8),
        circle(6, 17, 0.8),
        rect(10, 6.4, 8, 1.2, rx=0.4),
        rect(10, 16.4, 8, 1.2, rx=0.4),
    ]


def robot_glyph():
    return [
        round_rect(6, 6, 12, 11, 1.6),       # head/body
        circle(9, 10, 1.1),                   # left eye
        circle(15, 10, 1.1),                  # right eye
        rect(10, 13.5, 4, 1.0, rx=0.4),      # mouth
        rect(11.2, 3, 1.6, 3),                # antenna stem
        circle(12, 2.5, 1.0),                 # antenna ball
        rect(4, 11, 2, 4, rx=0.6),            # left ear
        rect(18, 11, 2, 4, rx=0.6),           # right ear
    ]


def calendar_glyph():
    return [
        round_rect(3, 5, 18, 16, 1.2),
        rect(3, 5, 18, 4),
        rect(7, 2.5, 1.6, 4, rx=0.5),
        rect(15.4, 2.5, 1.6, 4, rx=0.5),
        # day cells (small dots)
        circle(7, 13, 0.8), circle(11, 13, 0.8), circle(15, 13, 0.8),
        circle(7, 16.5, 0.8), circle(11, 16.5, 0.8),
    ]


def hand_glyph():
    """Stylized open hand."""
    return [
        path(
            "M 6 21 "
            "L 6 12 "
            "Q 6 10 8 10 "
            "Q 9.5 10 9.5 12 "
            "L 9.5 6 "
            "Q 9.5 4 11 4 "
            "Q 12.5 4 12.5 6 "
            "L 12.5 11 "
            "L 12.5 5 "
            "Q 12.5 3 14 3 "
            "Q 15.5 3 15.5 5 "
            "L 15.5 11 "
            "L 15.5 7 "
            "Q 15.5 5 17 5 "
            "Q 18.5 5 18.5 7 "
            "L 18.5 14 "
            "Q 18.5 21 12 21 Z"
        )
    ]


def briefcase_glyph():
    return [
        round_rect(2, 7, 20, 13, 1.5),
        path("M 9 7 L 9 5 Q 9 4 10 4 L 14 4 Q 15 4 15 5 L 15 7 L 13 7 L 13 5 L 11 5 L 11 7 Z"),
        rect(2, 12, 20, 1.4),
    ]


def book_glyph():
    return [
        path(
            "M 4 3 L 11 3 Q 12 3 12 4 L 12 21 Q 12 20 11 20 L 4 20 Z "
        ),
        path(
            "M 20 3 L 13 3 Q 12 3 12 4 L 12 21 Q 12 20 13 20 L 20 20 Z"
        ),
    ]


def bell_glyph():
    return [
        path(
            "M 12 3 "
            "C 8 3 6 6 6 10 "
            "L 6 14 "
            "L 4 17 "
            "L 20 17 "
            "L 18 14 "
            "L 18 10 "
            "C 18 6 16 3 12 3 Z"
        ),
        ellipse(12, 19, 2.2, 1.6),
    ]


def funnel_glyph():
    return [
        path(
            "M 3 4 "
            "L 21 4 "
            "L 14 13 "
            "L 14 21 "
            "L 10 19 "
            "L 10 13 Z"
        )
    ]


def link_glyph():
    return [
        path(
            "M 7 13 "
            "C 5 13 4 12 4 10 "
            "C 4 8 5 7 7 7 "
            "L 11 7 "
            "L 11 9 "
            "L 7 9 "
            "C 6 9 6 9.5 6 10 "
            "C 6 11 6 11 7 11 "
            "L 9 11 "
            "L 9 13 Z"
        ),
        path(
            "M 17 11 "
            "C 19 11 20 12 20 14 "
            "C 20 16 19 17 17 17 "
            "L 13 17 "
            "L 13 15 "
            "L 17 15 "
            "C 18 15 18 14.5 18 14 "
            "C 18 13 18 13 17 13 "
            "L 15 13 "
            "L 15 11 Z"
        ),
        rect(8, 11, 8, 2, rx=0.3),
    ]


def cycle_glyph(cx=12, cy=12, r=8):
    """Two arrows in a circular pattern -> cycle / refresh / loop."""
    # top half arrow (pointing right)
    parts = []
    parts.append(path(
        f"M {cx - r + 1.4} {cy - 1.6} "
        f"C {cx - r + 1.4} {cy - r + 1.4} {cx + r - 1.4} {cy - r + 1.4} {cx + r - 1.4} {cy - 1.6} "
        f"L {cx + r - 0.2} {cy - 1.6} "
        f"L {cx + r - 3.4} {cy - 4.6} "
        f"L {cx + r - 3.4} {cy - 0.2} "
        f"L {cx + r - 1.4} {cy + 0.2} "
        f"C {cx + r - 1.4} {cy - r + 2.6} {cx - r + 1.4} {cy - r + 2.6} {cx - r + 1.4} {cy + 0.2} Z",
        fill_rule="evenodd"
    ))
    # bottom half arrow (pointing left)
    parts.append(path(
        f"M {cx + r - 1.4} {cy + 1.6} "
        f"C {cx + r - 1.4} {cy + r - 1.4} {cx - r + 1.4} {cy + r - 1.4} {cx - r + 1.4} {cy + 1.6} "
        f"L {cx - r + 0.2} {cy + 1.6} "
        f"L {cx - r + 3.4} {cy + 4.6} "
        f"L {cx - r + 3.4} {cy + 0.2} "
        f"L {cx - r + 1.4} {cy - 0.2} "
        f"C {cx - r + 1.4} {cy + r - 2.6} {cx + r - 1.4} {cy + r - 2.6} {cx + r - 1.4} {cy - 0.2} Z",
        fill_rule="evenodd"
    ))
    return parts
