"""Emit a 24x24 viewBox SVG from a normalized list of parts.

Every part is rendered as a single <path>/<rect>/<ellipse>/<polygon> element
with the same fill color (default #2D3748). The icon is monochrome so it can
be re-tinted via the user's CSS / `fill` attribute / OOXML Shape Fill.
"""
from __future__ import annotations
from typing import Sequence

DEFAULT_FILL = "#2D3748"


def render_svg(parts: Sequence[dict], size: int = 24, fill: str = DEFAULT_FILL,
               title: str = "") -> str:
    body = []
    for p in parts:
        body.append(_part_to_svg(p))
    title_tag = f"<title>{_xml_escape(title)}</title>" if title else ""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'width="{size}" height="{size}" fill="{fill}">'
        f"{title_tag}"
        + "".join(body)
        + "</svg>"
    )


def _part_to_svg(p: dict) -> str:
    t = p["type"]
    if t == "rect":
        rx = p.get("rx", 0)
        rx_attr = f' rx="{_n(rx)}" ry="{_n(rx)}"' if rx else ""
        return (f'<rect x="{_n(p["x"])}" y="{_n(p["y"])}" '
                f'width="{_n(p["w"])}" height="{_n(p["h"])}"{rx_attr}/>')
    if t == "ellipse":
        return (f'<ellipse cx="{_n(p["cx"])}" cy="{_n(p["cy"])}" '
                f'rx="{_n(p["rx"])}" ry="{_n(p["ry"])}"/>')
    if t == "polygon":
        pts = " ".join(f"{_n(x)},{_n(y)}" for (x, y) in p["points"])
        return f'<polygon points="{pts}"/>'
    if t == "path":
        rule = p.get("fill_rule", "nonzero")
        rule_attr = f' fill-rule="{rule}"' if rule != "nonzero" else ""
        return f'<path d="{p["d"]}"{rule_attr}/>'
    raise ValueError(f"unrenderable part {t}")


def _n(v: float) -> str:
    if isinstance(v, int):
        return str(v)
    if abs(v - round(v)) < 1e-6:
        return str(int(round(v)))
    return f"{v:.3f}".rstrip("0").rstrip(".")


def _xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))
