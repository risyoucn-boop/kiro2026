"""Corner-badge modifiers used to generate semantic variants from each base.

Apply with `with_badge(parts, badge="check_tr")`. The base is shrunk toward
the opposite corner and the badge is overlaid in the freed corner.
"""
from __future__ import annotations

from primitives import scale_about, translate
from builders import (
    circle, line, path, rect, donut, polygon, star, check_mark,
    plus_cross, cross_x, exclam,
)


def _check_badge(cx=19, cy=5):
    return [
        line(cx - 2.2, cy + 0.2, cx - 0.6, cy + 1.6, w=1.7),
        line(cx - 0.6, cy + 1.6, cx + 2.4, cy - 1.6, w=1.7),
    ]


def _warn_badge(cx=19, cy=5):
    return [
        polygon([(cx, cy - 3), (cx + 3.0, cy + 2.4), (cx - 3.0, cy + 2.4)]),
    ] + _ko_inside_warn(cx, cy)


def _ko_inside_warn(cx, cy):
    # Use a tiny "punched" rectangle: same color as base means the bar
    # inside the triangle is visible only as positive space. To make a
    # readable '!' inside, we use evenodd subpaths.
    d = (
        # outer triangle
        f"M {cx} {cy - 3} L {cx + 3.0} {cy + 2.4} L {cx - 3.0} {cy + 2.4} Z "
        # inner '!' bar (reversed)
        f"M {cx + 0.4} {cy - 1.4} L {cx + 0.4} {cy + 0.6} L {cx - 0.4} {cy + 0.6} L {cx - 0.4} {cy - 1.4} Z "
        f"M {cx + 0.45} {cy + 1.4} L {cx + 0.45} {cy + 1.95} L {cx - 0.45} {cy + 1.95} L {cx - 0.45} {cy + 1.4} Z"
    )
    return [path(d, fill_rule="evenodd")]


def _warn_badge_full(cx=19, cy=5):
    """Filled triangle with knockout '!' (single combined path, evenodd)."""
    d = (
        f"M {cx} {cy - 3.2} L {cx + 3.2} {cy + 2.6} L {cx - 3.2} {cy + 2.6} Z "
        f"M {cx + 0.4} {cy - 1.4} L {cx + 0.4} {cy + 0.6} L {cx - 0.4} {cy + 0.6} L {cx - 0.4} {cy - 1.4} Z "
        f"M {cx + 0.45} {cy + 1.4} L {cx + 0.45} {cy + 1.95} L {cx - 0.45} {cy + 1.95} L {cx - 0.45} {cy + 1.4} Z"
    )
    return [path(d, fill_rule="evenodd")]


def _cross_badge(cx=19, cy=5):
    return cross_x(cx, cy, size=5.0, w=1.6)


def _plus_badge(cx=19, cy=5):
    return plus_cross(cx, cy, size=5.0, w=1.6)


def _minus_badge(cx=19, cy=5):
    return [rect(cx - 2.5, cy - 0.7, 5, 1.4, rx=0.4)]


def _eye_badge(cx=19, cy=5):
    # eye = small lens with pupil
    return [
        donut(cx, cy, 3.0, 2.1),
        circle(cx, cy, 1.0),
    ]


def _clock_badge(cx=19, cy=5):
    return [
        donut(cx, cy, 3.0, 2.2),
        line(cx, cy, cx + 1.5, cy, w=0.6),
        line(cx, cy, cx, cy - 1.6, w=0.6),
    ]


def _gear_badge(cx=19, cy=5):
    return [
        {"type": "gear", "cx": cx, "cy": cy, "r_outer": 3.0, "r_inner": 2.1, "hole_r": 0.9, "teeth": 6}
    ]


def _star_badge(cx=19, cy=5):
    return [star(cx, cy, 3.0, 1.3, points=5, rot=-90)]


def _smart_badge(cx=19, cy=5):
    """Sparkle / AI mark: a 4-point star (diamond)."""
    return [
        star(cx, cy, 3.2, 0.8, points=4, rot=-90),
        circle(cx + 4, cy + 2.8, 0.7),
        circle(cx - 3.8, cy - 2.6, 0.5),
    ]


def _lock_badge(cx=19, cy=5):
    return [
        rect(cx - 2.0, cy - 0.6, 4.0, 3.4, rx=0.6),
        path(
            f"M {cx - 1.3} {cy - 0.6} "
            f"L {cx - 1.3} {cy - 1.6} "
            f"C {cx - 1.3} {cy - 3.0} {cx + 1.3} {cy - 3.0} {cx + 1.3} {cy - 1.6} "
            f"L {cx + 1.3} {cy - 0.6} "
            f"L {cx + 0.5} {cy - 0.6} "
            f"L {cx + 0.5} {cy - 1.6} "
            f"C {cx + 0.5} {cy - 2.4} {cx - 0.5} {cy - 2.4} {cx - 0.5} {cy - 1.6} "
            f"L {cx - 0.5} {cy - 0.6} Z"
        ),
    ]


def _sync_badge(cx=19, cy=5):
    """Two opposed curved arrows (refresh)."""
    d = (
        f"M {cx - 2.6} {cy} "
        f"C {cx - 2.6} {cy - 3} {cx + 2.6} {cy - 3} {cx + 2.6} {cy} "
        f"L {cx + 3.5} {cy} "
        f"L {cx + 1.7} {cy + 2} "
        f"L {cx + 1.7} {cy + 0.6} "
        f"C {cx + 1.7} {cy - 1.4} {cx - 1.7} {cy - 1.4} {cx - 1.7} {cy + 0.6} Z"
    )
    return [path(d)]


def _arrow_up_badge(cx=19, cy=5):
    return [{"type": "arrow", "x1": cx, "y1": cy + 2.6, "x2": cx, "y2": cy - 2.6,
             "shaft_w": 1.2, "head_w": 3.0, "head_l": 2.4}]


def _arrow_down_badge(cx=19, cy=5):
    return [{"type": "arrow", "x1": cx, "y1": cy - 2.6, "x2": cx, "y2": cy + 2.6,
             "shaft_w": 1.2, "head_w": 3.0, "head_l": 2.4}]


def _person_badge(cx=19, cy=5):
    return [
        circle(cx, cy - 1.6, 1.2),
        path(
            f"M {cx - 2.4} {cy + 2.6} "
            f"C {cx - 2.4} {cy + 0.4} {cx + 2.4} {cy + 0.4} {cx + 2.4} {cy + 2.6} Z"
        ),
    ]


def _heart_badge(cx=19, cy=5):
    half = 2.6
    h = 2.4
    top = cy - h / 2
    d = (
        f"M {cx} {cy + h / 2} "
        f"C {cx - half * 1.1} {cy + h * 0.15} {cx - half} {top + h * 0.05} {cx - half * 0.55} {top + h * 0.05} "
        f"C {cx - half * 0.2} {top + h * 0.05} {cx} {top + h * 0.25} {cx} {top + h * 0.4} "
        f"C {cx} {top + h * 0.25} {cx + half * 0.2} {top + h * 0.05} {cx + half * 0.55} {top + h * 0.05} "
        f"C {cx + half} {top + h * 0.05} {cx + half * 1.1} {cy + h * 0.15} {cx} {cy + h / 2} Z"
    )
    return [path(d)]


# ---- registry ----

BADGES = {
    "check":    (_check_badge,        ("已验证", "Verified")),
    "warn":     (_warn_badge_full,    ("预警", "Alert")),
    "cross":    (_cross_badge,        ("失效", "Rejected")),
    "plus":     (_plus_badge,         ("新增", "Add")),
    "minus":    (_minus_badge,        ("减少", "Remove")),
    "lock":     (_lock_badge,         ("加锁", "Locked")),
    "eye":      (_eye_badge,          ("洞察", "Insight")),
    "clock":    (_clock_badge,        ("定时", "Scheduled")),
    "gear":     (_gear_badge,         ("可配置", "Configurable")),
    "sync":     (_sync_badge,         ("同步", "Sync")),
    "star":     (_star_badge,         ("重点", "Featured")),
    "smart":    (_smart_badge,        ("智能", "Smart")),
    "up":       (_arrow_up_badge,     ("上升", "Up")),
    "down":     (_arrow_down_badge,   ("下降", "Down")),
    "person":   (_person_badge,       ("协同", "WithPerson")),
    "heart":    (_heart_badge,        ("关怀", "Care")),
}


def with_badge(parts, badge: str, anchor: str = "tr", shrink: float = 0.78):
    """Return parts shrunk toward the opposite corner, with badge overlaid.

    anchor: 'tr' (top-right), 'tl', 'br', 'bl' — where the badge goes.
    """
    if badge not in BADGES:
        raise ValueError(f"unknown badge {badge}")
    fn, _label = BADGES[badge]

    if anchor == "tr":
        # base shrinks toward bottom-left: anchor = (0, 24)
        ax, ay = 0, 24
        bx, by = 19, 5
    elif anchor == "tl":
        ax, ay = 24, 24
        bx, by = 5, 5
    elif anchor == "br":
        ax, ay = 0, 0
        bx, by = 19, 19
    elif anchor == "bl":
        ax, ay = 24, 0
        bx, by = 5, 19
    else:
        raise ValueError(anchor)

    shrunk = scale_about(parts, shrink, shrink, ax, ay)
    badge_parts = fn(bx, by)
    return list(shrunk) + list(badge_parts)


def label_for(badge: str) -> tuple[str, str]:
    return BADGES[badge][1]
