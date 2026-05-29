# 科幻小说大冒险 · Grade 6 PPT 工程

一套用 **Node.js + PptxGenJS** 自动生成的小学六年级"科幻小说分享"演讲 PPT。

> 主题：《科幻小说大冒险：种类、结构和有趣的科学设定》
> 核心主线：科幻 = 一个疯狂的设定 + 一步一步推下去 + 看人物怎么选择。
> 演讲时长：10–15 分钟（默认按 12 分钟设计）。
> 输出文件：`output/science_fiction_adventure_grade6.pptx`（16:9，共 12 页）。

---

## 1. 如何安装依赖

需要先安装 **Node.js 18+**（推荐 20 或 22）。然后在本工程目录下：

```bash
npm install
```

主要依赖：
- [`pptxgenjs`](https://www.npmjs.com/package/pptxgenjs)：PPTX 生成库
- [`sharp`](https://www.npmjs.com/package/sharp)：把 SVG 素材转成 PNG，保证在 PowerPoint / Keynote / WPS / 投影仪都能稳定显示

---

## 2. 如何生成 PPTX

```bash
npm run build
```

成功后控制台会输出：

```
[OK] PPTX generated at: .../output/science_fiction_adventure_grade6.pptx
```

其它命令：

```bash
npm run clean     # 删除已生成的 PPTX
npm run rebuild   # 先清理再重新生成
```

---

## 3. 输出文件在哪里

```
scifi-grade6-ppt/
├── output/
│   └── science_fiction_adventure_grade6.pptx   <-- 这就是最终课堂用 PPT
```

直接双击就能用 PowerPoint / Keynote / WPS 打开和编辑。
**文件名是英文，方便跨平台、上传校园系统。**

---

## 4. 项目结构

```
scifi-grade6-ppt/
├── package.json                       # 脚本与依赖
├── README.md                          # 本说明
├── generate_scifi_grade6_ppt.js       # 主生成脚本
├── QA_CHECKLIST.md                    # 自检报告
├── assets/                            # 本地 SVG 素材（10 个）
│   ├── rocket.svg
│   ├── planet.svg
│   ├── robot.svg
│   ├── talking_bag.svg
│   ├── memory_disk.svg
│   ├── emotion_sweater.svg
│   ├── speed_button.svg
│   ├── dream_app.svg
│   ├── brain_interface.svg
│   ├── story_formula.svg
│   └── .png_cache/                    # 构建时自动生成的 PNG 缓存
├── notes/
│   ├── speaker_notes.md               # 演讲稿（每页一段，含动作 / 停顿 / 互动 / 备用话术）
│   └── rehearsal_guide.md             # 三遍练习法 + 上台前清单 + 救场技巧
└── output/
    └── science_fiction_adventure_grade6.pptx
```

---

## 5. 如何修改文案

打开 `generate_scifi_grade6_ppt.js`，每一页都用注释划好了块：

```js
// SLIDE 5 — Core formula
{
  const s = pres.addSlide();
  ...
}
```

- **改标题**：在 `addTitle(s, "...")` 这一行直接改。
- **改正文**：在每个 `s.addText("...")` 或 `addStepCard(...)` 里改文字。
- **改记忆点**：搜 `addMemoryPoint(`，改后面那句话。
- **改互动提示**：搜 `addInteractionBadge(`。
- **改演讲稿（备注页）**：搜 `addSpeakerNote(`。

> 每页正文不要超过 5 条，每行不要超过 18 个中文字符——这是为投影可读性专门设计的。

改完保存，再跑：

```bash
npm run rebuild
```

---

## 6. 如何修改颜色和字体

所有颜色、字体都集中在 `generate_scifi_grade6_ppt.js` 顶部：

```js
const COLORS = {
  deepSpace:   "16213E", // 深空蓝
  starPurple:  "5B4B8A", // 星空紫
  techCyan:    "4DD0E1", // 科技青
  warmYellow:  "FFC857", // 暖橙黄
  brightGreen: "7ED957", // 亮绿
  cloudWhite:  "F8FAFF", // 云朵白
  coralRed:    "FF6B6B",
  ...
};

const FONT_TITLE = "Microsoft YaHei";
const FONT_BODY  = "Microsoft YaHei";
```

- **换主色**：把 `warmYellow` 改成你想要的 6 位 HEX（不带 `#`），全场强调色都会跟着变。
- **换字体**：改 `FONT_TITLE` / `FONT_BODY`。建议用系统自带字体：
  - Windows：`Microsoft YaHei`、`SimHei`
  - macOS：`PingFang SC`、`Heiti SC`
  - WPS：`Microsoft YaHei` 通用兼容
- 改完保存后 `npm run rebuild` 即可。

---

## 7. 我可以替换 SVG 素材吗？

可以。把同名的 SVG 文件丢进 `assets/` 覆盖即可，下次构建会自动重新转 PNG。

> 推荐：保持扁平插画 + 圆角风，配色不要太深，整体亮一点更适合六年级。

---

## 8. 演讲稿 / 练习指南在哪里？

| 文件 | 用途 |
|------|------|
| `notes/speaker_notes.md` | 12 页 × 全套讲稿，含动作、停顿、互动、冷场备用、收束话术 |
| `notes/rehearsal_guide.md` | 三遍练习法、上台前 5 分钟清单、忘词救场、控场技巧 |

> 我们没有把讲稿“硬塞进 PPT 备注页”，而是写在独立 Markdown 里。
> 这样改起来方便，也不依赖各个版本 PptxGenJS 的备注页支持稳定性。
> （脚本里仍然会调用 `addNotes`，所以 PPT 里也带了一份备份版本。）

---

## 9. 常见问题

**Q：在 macOS 上中文字体看起来不太对？**
A：把 `FONT_TITLE` / `FONT_BODY` 改成 `"PingFang SC"`，重新构建。

**Q：PPT 打开后图标变成红叉？**
A：因为旧版 Office 不支持 SVG。本工程**已经把 SVG 转成 PNG**再嵌入，所以不会出现这种情况。如果替换了素材，记得跑 `npm run rebuild`。

**Q：能不能加更多页？**
A：能。在 `generate_scifi_grade6_ppt.js` 里仿照已有的 `// SLIDE N — ...` 块，复制一份改文案即可。

---

## 10. License

MIT。素材均为本工程现场绘制的 SVG，无版权图片，可自由用于课堂教学和分享。
