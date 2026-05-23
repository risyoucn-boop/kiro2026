"""Reusable framework patterns for consulting-style icons.

These helpers compose primitives into the recurring structures you see in
strategy decks: 2x2 matrices, pyramids, S-curves, radial hub-spoke, etc.

All output uses the standard 24x24 logical grid.
"""
from __future__ import annotations
import math
from typing import Iterable

from builders import (
    rect, circle, ellipse, line, polygon, path, donut, star, arrow,
    round_rect, diamond,
)


# ----- matrices --------------------------------------------------------

def matrix_2x2(highlight=None, axis=True):
    """4-cell 2x2 matrix. highlight = 'tl'|'tr'|'bl'|'br'|None or list of those.
    axis=True draws thin axis arrows on left/bottom."""
    parts = []
    cells = {
        "tl": (3, 3, 8.5, 8.5),
        "tr": (12.5, 3, 8.5, 8.5),
        "bl": (3, 12.5, 8.5, 8.5),
        "br": (12.5, 12.5, 8.5, 8.5),
    }
    hl = set(highlight) if isinstance(highlight, (list, tuple)) else ({highlight} if highlight else set())
    for k, (x, y, w, h) in cells.items():
        if k in hl:
            parts.append(rect(x, y, w, h, rx=0.6))
        else:
            # outline-only via donut-like approach (frame)
            parts.append(rect(x, y, w, 0.6))             # top
            parts.append(rect(x, y + h - 0.6, w, 0.6))   # bottom
            parts.append(rect(x, y, 0.6, h))             # left
            parts.append(rect(x + w - 0.6, y, 0.6, h))   # right
    if axis:
        parts.append(arrow(2.5, 21.5, 2.5, 1.5, shaft_w=0.4, head_w=1.4, head_l=1.0))
        parts.append(arrow(2.5, 21.5, 22.5, 21.5, shaft_w=0.4, head_w=1.4, head_l=1.0))
    return parts


def matrix_3x3(highlight=None):
    parts = []
    size = 6
    gap = 0.5
    start = 3
    for r in range(3):
        for c in range(3):
            x = start + c * (size + gap)
            y = start + r * (size + gap)
            cell = (r, c)
            if highlight and cell in highlight:
                parts.append(rect(x, y, size, size, rx=0.4))
            else:
                parts.append(rect(x, y, size, 0.5))
                parts.append(rect(x, y + size - 0.5, size, 0.5))
                parts.append(rect(x, y, 0.5, size))
                parts.append(rect(x + size - 0.5, y, 0.5, size))
    return parts


def matrix_grid(rows, cols, highlight_cells=None):
    """Generic R x C matrix, smaller cells for higher counts."""
    parts = []
    margin = 2
    inner = 24 - 2 * margin
    total_gap = (cols - 1) * 0.4
    cell_w = (inner - total_gap) / cols
    total_gap_v = (rows - 1) * 0.4
    cell_h = (inner - total_gap_v) / rows
    hl = set(highlight_cells or [])
    for r in range(rows):
        for c in range(cols):
            x = margin + c * (cell_w + 0.4)
            y = margin + r * (cell_h + 0.4)
            if (r, c) in hl:
                parts.append(rect(x, y, cell_w, cell_h, rx=0.3))
            else:
                t = 0.4
                parts.append(rect(x, y, cell_w, t))
                parts.append(rect(x, y + cell_h - t, cell_w, t))
                parts.append(rect(x, y, t, cell_h))
                parts.append(rect(x + cell_w - t, y, t, cell_h))
    return parts


# ----- pyramid / hierarchy --------------------------------------------

def pyramid_n(levels=4, gap=0.4):
    """Stacked-trapezoid pyramid with N levels."""
    parts = []
    top_y = 3
    bot_y = 21
    cx = 12
    apex_w = 2  # width at top of top level
    base_w = 18 # width at bottom of bottom level
    h_total = bot_y - top_y
    h_per = (h_total - (levels - 1) * gap) / levels
    for i in range(levels):
        y0 = top_y + i * (h_per + gap)
        y1 = y0 + h_per
        # widths via lerp from apex_w to base_w
        t0 = i / levels
        t1 = (i + 1) / levels
        w0 = apex_w + (base_w - apex_w) * t0
        w1 = apex_w + (base_w - apex_w) * t1
        parts.append(polygon([
            (cx - w0 / 2, y0), (cx + w0 / 2, y0),
            (cx + w1 / 2, y1), (cx - w1 / 2, y1),
        ]))
    return parts


def pyramid_inverted(levels=3, gap=0.4):
    """Inverted pyramid (servant leadership / funnel-shape)."""
    parts = []
    top_y = 3
    bot_y = 21
    cx = 12
    base_w = 18
    apex_w = 2
    h_total = bot_y - top_y
    h_per = (h_total - (levels - 1) * gap) / levels
    for i in range(levels):
        y0 = top_y + i * (h_per + gap)
        y1 = y0 + h_per
        t0 = i / levels
        t1 = (i + 1) / levels
        w0 = base_w + (apex_w - base_w) * t0
        w1 = base_w + (apex_w - base_w) * t1
        parts.append(polygon([
            (cx - w0 / 2, y0), (cx + w0 / 2, y0),
            (cx + w1 / 2, y1), (cx - w1 / 2, y1),
        ]))
    return parts


# ----- curves ----------------------------------------------------------

def s_curve(x0=3, y0=20, x1=21, y1=4, w=1.6):
    """A single S-curve as a thick filled path."""
    # Use cubic bezier for the centerline, render as filled stroke band
    # Top edge
    return [path(
        f"M {x0} {y0 + w/2} "
        f"C {x0 + 6} {y0 + w/2}  {x1 - 6} {y1 + w/2}  {x1} {y1 + w/2} "
        f"L {x1} {y1 - w/2} "
        f"C {x1 - 6} {y1 - w/2}  {x0 + 6} {y0 - w/2}  {x0} {y0 - w/2} Z"
    )]


def hockey_stick(x0=3, y0=21, x1=21, y1=4):
    """Flat then sharp upward — as filled stroke."""
    w = 1.6
    return [path(
        f"M {x0} {y0} "
        f"L {x0 + 10} {y0} "
        f"L {x0 + 10} {y0 - w} "
        f"C {x0 + 12} {y0 - w}  {x1 - 1} {y1}  {x1} {y1} "
        f"L {x1} {y1 + w} "
        f"C {x1 - 2} {y1 + w}  {x0 + 12} {y0 - 0.4}  {x0 + 10 + w} {y0 - 0.4} "
        f"L {x0} {y0 - 0.4} Z"
    )]


def exponential_curve(x0=3, y0=21, x1=21, y1=4, w=1.5):
    return [path(
        f"M {x0} {y0} "
        f"C {x0 + 8} {y0}  {x1 - 5} {y1 + 7}  {x1} {y1} "
        f"L {x1} {y1 + w} "
        f"C {x1 - 5} {y1 + 7 + w}  {x0 + 8} {y0 + w}  {x0} {y0 + w} Z"
    )]


def bell_curve(cx=12, baseline=20, height=14, width=20, w=1.4):
    """Normal-distribution bell as filled outline."""
    half = width / 2
    top_y = baseline - height
    return [path(
        # outer
        f"M {cx - half} {baseline} "
        f"C {cx - half} {baseline - height * 0.2}  {cx - half * 0.5} {top_y}  {cx} {top_y} "
        f"C {cx + half * 0.5} {top_y}  {cx + half} {baseline - height * 0.2}  {cx + half} {baseline} "
        # inner offset
        f"L {cx + half - w} {baseline} "
        f"C {cx + half - w} {baseline - height * 0.2 + w * 0.5}  {cx + half * 0.5 - w * 0.4} {top_y + w * 1.5}  {cx} {top_y + w * 1.5} "
        f"C {cx - half * 0.5 + w * 0.4} {top_y + w * 1.5}  {cx - half + w} {baseline - height * 0.2 + w * 0.5}  {cx - half + w} {baseline} Z"
    ), rect(2, baseline, 20, 1, rx=0.2)]


# ----- radial / hub-spoke ---------------------------------------------

def radial_n(n=5, r_outer=10, node_r=2.4, with_center=True, center_r=2.6):
    """N satellites around an optional central node."""
    parts = []
    cx, cy = 12, 12
    if with_center:
        parts.append(circle(cx, cy, center_r))
    angles = [-90 + i * (360 / n) for i in range(n)]
    for a in angles:
        rad = a * math.pi / 180
        x = cx + r_outer * math.cos(rad)
        y = cy + r_outer * math.sin(rad)
        # connector line
        if with_center:
            parts.append(line(cx, cy, x, y, w=0.5))
        parts.append(circle(x, y, node_r))
    return parts


def concentric_rings(n=4, r_max=10, ring_w=0.8):
    parts = []
    cx, cy = 12, 12
    step = (r_max - 1) / n
    for i in range(n):
        r_outer = r_max - i * step
        r_inner = r_outer - ring_w
        if r_inner > 0:
            parts.append(donut(cx, cy, r_outer, r_inner))
    parts.append(circle(cx, cy, 1.2))
    return parts


# ----- flows -----------------------------------------------------------

def flow_chain(n=5, with_arrows=True, shape="circle"):
    """Horizontal chain of N nodes connected by arrows."""
    parts = []
    cy = 12
    margin = 2
    node_r = min(1.8, (24 - 2 * margin) / (n * 3))
    spacing = (24 - 2 * margin) / n
    for i in range(n):
        x = margin + spacing * (i + 0.5)
        if shape == "circle":
            parts.append(circle(x, cy, node_r))
        elif shape == "square":
            parts.append(rect(x - node_r, cy - node_r, node_r * 2, node_r * 2, rx=0.3))
        elif shape == "diamond":
            parts.append(diamond(x, cy, node_r))
        if with_arrows and i < n - 1:
            x_next = margin + spacing * (i + 1.5)
            parts.append(arrow(x + node_r + 0.2, cy, x_next - node_r - 0.2, cy,
                               shaft_w=0.5, head_w=1.4, head_l=1.0))
    return parts


def stairs(n=5, direction="up"):
    """Stair-step shape with N levels."""
    parts = []
    margin = 2
    inner = 24 - 2 * margin
    step_w = inner / n
    step_h = (24 - 2 * margin) / n
    parts.append(rect(margin, 24 - margin - 1, inner, 1, rx=0.2))  # baseline
    for i in range(n):
        if direction == "up":
            h = step_h * (i + 1)
        else:
            h = step_h * (n - i)
        x = margin + i * step_w
        y = (24 - margin) - h
        parts.append(rect(x, y, step_w - 0.4, h, rx=0.3))
    return parts


def waterfall_bars(values=(3, 1, -1, 2, -1, 4)):
    """Waterfall chart bars: positive bars build up, negative come down.
    Returns bars at correct y-positions to simulate cumulative flow."""
    parts = []
    margin = 2
    inner_w = 24 - 2 * margin
    bar_w = inner_w / len(values) - 0.4
    baseline = 21
    scale = 2.0  # units of y per value
    cum = 0
    for i, v in enumerate(values):
        x = margin + i * (bar_w + 0.4)
        if v > 0:
            y_top = baseline - (cum + v) * scale
            y_bot = baseline - cum * scale
        else:
            y_top = baseline - cum * scale
            y_bot = baseline - (cum + v) * scale
        parts.append(rect(x, y_top, bar_w, abs(y_bot - y_top), rx=0.2))
        cum += v
    parts.append(rect(2, baseline, 20, 0.5, rx=0.1))
    return parts


# ----- venn / overlap --------------------------------------------------

def venn_2(rx=6.5, ry=6.5, gap=4.5):
    """Two-circle overlap (Venn)."""
    cy = 12
    return [
        donut(12 - gap, cy, rx, rx - 1.0),
        donut(12 + gap, cy, rx, rx - 1.0),
    ]


def venn_3():
    """Three-circle overlap."""
    r = 5.5
    centers = [
        (12, 8),
        (8, 15),
        (16, 15),
    ]
    return [donut(cx, cy, r, r - 1.0) for cx, cy in centers]


# ----- arrows / cycle --------------------------------------------------

def arrow_circle_4(cx=12, cy=12, r_outer=10, r_inner=7):
    """Four arrows arranged in a circular cycle (PDCA-style)."""
    parts = []
    # build 4 quarter-arrows
    # We approximate each as a thick arc segment with a triangular head
    for i in range(4):
        a_start = -90 + i * 90 + 6     # slight gap
        a_end = -90 + (i + 1) * 90 - 12
        # arc segment as path
        parts.append(_arc_arrow(cx, cy, r_outer, r_inner, a_start, a_end))
    return parts


def _arc_arrow(cx, cy, r_outer, r_inner, a_start_deg, a_end_deg):
    """Filled arc segment with a triangular arrowhead at end angle.
    Approximation using cubic beziers."""
    a0 = a_start_deg * math.pi / 180
    a1 = a_end_deg * math.pi / 180
    # approximate arc with ~4-segment polyline for simplicity
    n_segs = 6
    pts_outer = []
    pts_inner = []
    for i in range(n_segs + 1):
        t = i / n_segs
        a = a0 + (a1 - a0) * t
        pts_outer.append((cx + r_outer * math.cos(a), cy + r_outer * math.sin(a)))
        pts_inner.append((cx + r_inner * math.cos(a), cy + r_inner * math.sin(a)))
    # arrowhead at end (extend a bit)
    a_tip = a1 + (8 * math.pi / 180)
    r_mid = (r_outer + r_inner) / 2
    tip = (cx + (r_outer + 1.5) * math.cos(a_tip), cy + (r_outer + 1.5) * math.sin(a_tip))
    head_outer = (cx + (r_outer + 1.5) * math.cos(a1), cy + (r_outer + 1.5) * math.sin(a1))
    head_inner = (cx + (r_inner - 1.5) * math.cos(a1), cy + (r_inner - 1.5) * math.sin(a1))
    pts = pts_outer + [head_outer, tip, head_inner] + list(reversed(pts_inner))
    return polygon(pts)


def cycle_arrows_n(n=4, r_outer=10, r_inner=7):
    return arrow_circle_4()  # default 4; if n!=4, build similar
