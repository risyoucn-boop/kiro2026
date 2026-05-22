# Emojiall Scraper

Scrapes the Traditional-Chinese emoji directory at
[emojiall.com/zh-hant](https://www.emojiall.com/zh-hant) and writes the result
to `emojiall_zh_hant_emojis.xlsx` at the repo root.

## Output schema

The workbook has a single sheet with seven columns (matching the user-supplied
reference image):

| 列 | 名称 | 说明 |
|----|------|------|
| A  | 序号        | 1-based row index |
| B  | Emoji       | The emoji character |
| C  | 中文名      | 簡短名稱 from the emojiall page |
| D  | 场景章节    | `<主分类> / <子分类>` (e.g. `物品 / 辦公`) |
| E  | 建议用法    | First paragraph of 意義與描述, capped at ~280 chars |
| F  | 关键词      | 關鍵字 list, joined with the Chinese comma `、` |
| G  | Code Point  | `U+XXXX [U+YYYY ...]` computed from the emoji char itself |

## Running

```bash
pip install requests beautifulsoup4 lxml openpyxl
python3 scripts/scrape_emojis.py
```

The scraper is incremental: it caches `data/listing.json` (category listings)
and `data/details.json` (per-emoji detail pages) so repeated runs only refetch
URLs that previously failed.

A typical full run downloads ~1858 emoji pages with 20 worker threads and
finishes in roughly 5 minutes on an open network.
