"""Expand the base catalog to ~1000 IconDef entries by applying per-category
modifier badges to each base. Each result has full metadata.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from bases import CATEGORIES, CATEGORY_BADGES
from modifiers import with_badge, label_for


# Per-category, only use the first N badges, to land near 1000 total.
# DATA gets 5 badges (15 bases × 6 = 90), others get 5 each (14 × 6 = 84) -> 90 + 11*84 = 1014.
# We then trim down to exactly 1000 by dropping the last 14 expanded variants.

BADGES_PER_CAT = 5
TARGET_TOTAL = 1000


@dataclass
class IconDef:
    code: str
    cat_code: str
    cat_name: str
    cn_name: str
    en_name: str
    parts: list
    metaphor: str
    usage: str
    keywords_cn: list = field(default_factory=list)
    keywords_en: list = field(default_factory=list)
    base_key: str = ""
    badge: str = ""              # "" for plain
    license_note: str = "原创设计 · 可商用 · 形状非 SVG · 单色 PowerPoint Shape"


def build_all() -> list[IconDef]:
    out: list[IconDef] = []
    for cat_code, cat_name, base_list in CATEGORIES:
        badges = CATEGORY_BADGES[cat_code][:BADGES_PER_CAT]
        idx = 1
        for base in base_list:
            key, cn, en, fn, metaphor, usage, kw_cn, kw_en = base

            # plain
            out.append(IconDef(
                code=f"{cat_code}-{idx:03d}",
                cat_code=cat_code,
                cat_name=cat_name,
                cn_name=cn,
                en_name=en,
                parts=fn(),
                metaphor=metaphor,
                usage=usage,
                keywords_cn=list(kw_cn),
                keywords_en=list(kw_en),
                base_key=key,
                badge="",
            ))
            idx += 1

            # badged variants
            for b in badges:
                cn_suf, en_suf = label_for(b)
                out.append(IconDef(
                    code=f"{cat_code}-{idx:03d}",
                    cat_code=cat_code,
                    cat_name=cat_name,
                    cn_name=f"{cn}·{cn_suf}",
                    en_name=f"{en}{en_suf}",
                    parts=with_badge(fn(), b, "tr"),
                    metaphor=f"{metaphor}（{cn_suf}变体）",
                    usage=f"{usage}（{cn_suf}场景）",
                    keywords_cn=list(kw_cn) + [cn_suf],
                    keywords_en=list(kw_en) + [en_suf.lower()],
                    base_key=key,
                    badge=b,
                ))
                idx += 1

    # Trim down to exactly TARGET_TOTAL by removing from each category's
    # tail in round-robin order, so the cut spreads evenly.
    overflow = len(out) - TARGET_TOTAL
    if overflow > 0:
        cat_codes = [c[0] for c in CATEGORIES]
        # build per-cat indices in reverse (tail first)
        per_cat_tail: dict[str, list[int]] = {c: [] for c in cat_codes}
        for i, ic in enumerate(out):
            per_cat_tail[ic.cat_code].append(i)
        for c in cat_codes:
            per_cat_tail[c] = list(reversed(per_cat_tail[c]))

        drop: set[int] = set()
        cidx = 0
        # drop from largest categories first (DATA has 90, etc.)
        # Sort categories by size desc
        order = sorted(cat_codes, key=lambda c: len(per_cat_tail[c]), reverse=True)
        i = 0
        while overflow > 0:
            c = order[i % len(order)]
            tail = per_cat_tail[c]
            # only drop badged variants, not the plain (skip if already at base)
            while tail:
                idx = tail.pop(0)
                if out[idx].badge != "":
                    drop.add(idx)
                    overflow -= 1
                    break
            i += 1
            if i > 10000:
                break

        out = [ic for j, ic in enumerate(out) if j not in drop]

    return _renumber(out)


def _renumber(icons: list[IconDef]) -> list[IconDef]:
    """Renumber within each category after trimming."""
    by_cat: dict[str, int] = {}
    for ic in icons:
        n = by_cat.get(ic.cat_code, 0) + 1
        by_cat[ic.cat_code] = n
        ic.code = f"{ic.cat_code}-{n:03d}"
    return icons


if __name__ == "__main__":
    icons = build_all()
    print(f"Total icons: {len(icons)}")
    by_cat: dict[str, int] = {}
    for ic in icons:
        by_cat[ic.cat_code] = by_cat.get(ic.cat_code, 0) + 1
    for k, v in by_cat.items():
        print(f"  {k}: {v}")
    print("First 5:")
    for ic in icons[:5]:
        print(f"  {ic.code}\t{ic.cn_name}\t({ic.en_name})")
    print("Last 5:")
    for ic in icons[-5:]:
        print(f"  {ic.code}\t{ic.cn_name}\t({ic.en_name})")
