/**
 * generate_scifi_grade6_ppt.js
 *
 * Generates `output/science_fiction_adventure_grade6.pptx` — a 12-slide
 * sci-fi sharing presentation for grade-6 students.
 *
 * Run:  npm run build
 */

const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

// ---------------------------------------------------------------------------
// Theme — colors, fonts, layout
// ---------------------------------------------------------------------------
const COLORS = {
  deepSpace:   "16213E", // 深空蓝
  starPurple:  "5B4B8A", // 星空紫
  techCyan:    "4DD0E1", // 科技青
  warmYellow:  "FFC857", // 暖橙黄
  brightGreen: "7ED957", // 亮绿
  cloudWhite:  "F8FAFF", // 云朵白
  coralRed:    "FF6B6B", // 强调红
  inkBlack:    "1A1A2E",
  softGrey:    "E8ECF5",
};

const FONT_TITLE = "Microsoft YaHei";   // fallback safe on most systems
const FONT_BODY  = "Microsoft YaHei";

// 16:9 — pptxgenjs LAYOUT_WIDE is 13.333 x 7.5 inches
const SLIDE_W = 13.333;
const SLIDE_H = 7.5;

// ---------------------------------------------------------------------------
// SVG -> PNG conversion (sharp)
// ---------------------------------------------------------------------------
const sharp = require("sharp");

const ASSETS_DIR = path.join(__dirname, "assets");
const PNG_CACHE  = path.join(__dirname, "assets", ".png_cache");
if (!fs.existsSync(PNG_CACHE)) fs.mkdirSync(PNG_CACHE, { recursive: true });

async function svgToPng(svgFileName, widthPx = 800) {
  const svgPath = path.join(ASSETS_DIR, svgFileName);
  const pngPath = path.join(PNG_CACHE, svgFileName.replace(/\.svg$/i, ".png"));
  const svgBuf  = fs.readFileSync(svgPath);
  await sharp(svgBuf, { density: 300 })
    .resize({ width: widthPx })
    .png({ compressionLevel: 9 })
    .toFile(pngPath);
  return pngPath;
}

async function prepareAssets() {
  const files = [
    "rocket.svg",
    "planet.svg",
    "robot.svg",
    "talking_bag.svg",
    "memory_disk.svg",
    "emotion_sweater.svg",
    "speed_button.svg",
    "dream_app.svg",
    "brain_interface.svg",
    "story_formula.svg",
  ];
  const map = {};
  for (const f of files) {
    const w = f === "story_formula.svg" ? 1200 : 600;
    map[f] = await svgToPng(f, w);
  }
  return map;
}

// ---------------------------------------------------------------------------
// Helper functions (as required by the spec)
// ---------------------------------------------------------------------------
function addStarBackground(slide, variant = "deep") {
  // Solid background color
  const bg = variant === "light" ? COLORS.cloudWhite : COLORS.deepSpace;
  slide.background = { color: bg };

  if (variant === "light") {
    // soft top band
    slide.addShape("rect", {
      x: 0, y: 0, w: SLIDE_W, h: 0.9,
      fill: { color: COLORS.starPurple },
      line: { color: COLORS.starPurple },
    });
    return;
  }

  // Sprinkle stars (small white/yellow dots)
  const stars = [
    { x: 0.5, y: 0.6, c: COLORS.warmYellow },
    { x: 1.4, y: 1.3, c: COLORS.cloudWhite },
    { x: 2.9, y: 0.8, c: COLORS.techCyan },
    { x: 4.6, y: 0.4, c: COLORS.cloudWhite },
    { x: 6.4, y: 1.1, c: COLORS.warmYellow },
    { x: 8.2, y: 0.5, c: COLORS.cloudWhite },
    { x: 10.1, y: 1.0, c: COLORS.techCyan },
    { x: 11.6, y: 0.6, c: COLORS.warmYellow },
    { x: 12.5, y: 1.5, c: COLORS.cloudWhite },
    { x: 0.8, y: 6.6, c: COLORS.cloudWhite },
    { x: 2.3, y: 7.0, c: COLORS.warmYellow },
    { x: 5.0, y: 6.8, c: COLORS.techCyan },
    { x: 7.6, y: 7.1, c: COLORS.cloudWhite },
    { x: 9.8, y: 6.5, c: COLORS.warmYellow },
    { x: 12.0, y: 6.9, c: COLORS.cloudWhite },
  ];
  stars.forEach(s => {
    slide.addShape("ellipse", {
      x: s.x, y: s.y, w: 0.08, h: 0.08,
      fill: { color: s.c }, line: { color: s.c },
    });
  });

  if (variant === "deep" || variant === "purple") {
    slide.addShape("rect", {
      x: 0, y: 2.0, w: SLIDE_W, h: 5.5,
      fill: { color: variant === "purple" ? COLORS.starPurple : COLORS.deepSpace },
      line: { color: "FFFFFF", transparency: 100 },
    });
  }
}

function addTitle(slide, title, subtitle) {
  // Title chip / banner
  slide.addShape("roundRect", {
    x: 0.5, y: 0.35, w: 12.3, h: 1.0,
    fill: { color: COLORS.warmYellow },
    line: { color: COLORS.deepSpace, width: 2 },
    rectRadius: 0.18,
  });
  slide.addText(title, {
    x: 0.7, y: 0.4, w: 11.9, h: 0.9,
    fontFace: FONT_TITLE, fontSize: 32, bold: true,
    color: COLORS.deepSpace, align: "left", valign: "middle",
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.7, y: 1.5, w: 12.0, h: 0.45,
      fontFace: FONT_BODY, fontSize: 18, italic: true,
      color: COLORS.cloudWhite,
    });
  }
}

function addSticker(slide, text, x, y, w, h, color = COLORS.coralRed) {
  slide.addShape("roundRect", {
    x, y, w, h,
    fill: { color },
    line: { color: COLORS.deepSpace, width: 2 },
    rectRadius: 0.12,
  });
  slide.addText(text, {
    x, y, w, h,
    fontFace: FONT_TITLE, fontSize: 16, bold: true,
    color: COLORS.deepSpace, align: "center", valign: "middle",
  });
}

function addSpeechBubble(slide, text, x, y, w, h) {
  slide.addShape("roundRect", {
    x, y, w, h,
    fill: { color: COLORS.cloudWhite },
    line: { color: COLORS.deepSpace, width: 3 },
    rectRadius: 0.25,
  });
  // bubble tail
  slide.addShape("triangle", {
    x: x + 0.3, y: y + h - 0.05, w: 0.4, h: 0.35,
    fill: { color: COLORS.cloudWhite },
    line: { color: COLORS.deepSpace, width: 3 },
    rotate: 180,
  });
  slide.addText(text, {
    x: x + 0.2, y: y + 0.15, w: w - 0.4, h: h - 0.3,
    fontFace: FONT_BODY, fontSize: 18, bold: true,
    color: COLORS.deepSpace, align: "center", valign: "middle",
  });
}

function addStepCard(slide, stepTitle, text, x, y, w, h, color = COLORS.techCyan) {
  // Card shadow
  slide.addShape("roundRect", {
    x: x + 0.08, y: y + 0.08, w, h,
    fill: { color: COLORS.deepSpace, transparency: 60 },
    line: { color: COLORS.deepSpace, transparency: 100 },
    rectRadius: 0.2,
  });
  // Card body
  slide.addShape("roundRect", {
    x, y, w, h,
    fill: { color: COLORS.cloudWhite },
    line: { color: COLORS.deepSpace, width: 3 },
    rectRadius: 0.2,
  });
  // Header strip
  slide.addShape("roundRect", {
    x, y, w, h: 0.7,
    fill: { color },
    line: { color: COLORS.deepSpace, width: 3 },
    rectRadius: 0.2,
  });
  slide.addText(stepTitle, {
    x, y, w, h: 0.7,
    fontFace: FONT_TITLE, fontSize: 20, bold: true,
    color: COLORS.deepSpace, align: "center", valign: "middle",
  });
  slide.addText(text, {
    x: x + 0.2, y: y + 0.85, w: w - 0.4, h: h - 1.0,
    fontFace: FONT_BODY, fontSize: 16,
    color: COLORS.deepSpace, align: "left", valign: "top",
    paraSpaceAfter: 6,
  });
}

function addInteractionBadge(slide, text) {
  // pinned at bottom-right
  slide.addShape("roundRect", {
    x: 8.5, y: 6.55, w: 4.5, h: 0.7,
    fill: { color: COLORS.brightGreen },
    line: { color: COLORS.deepSpace, width: 2 },
    rectRadius: 0.35,
  });
  slide.addText("互动 · " + text, {
    x: 8.5, y: 6.55, w: 4.5, h: 0.7,
    fontFace: FONT_TITLE, fontSize: 15, bold: true,
    color: COLORS.deepSpace, align: "center", valign: "middle",
  });
}

function addMemoryPoint(slide, text) {
  // pinned at bottom-left
  slide.addShape("roundRect", {
    x: 0.4, y: 6.55, w: 7.8, h: 0.7,
    fill: { color: COLORS.warmYellow },
    line: { color: COLORS.deepSpace, width: 2 },
    rectRadius: 0.35,
  });
  slide.addText("记忆点 · " + text, {
    x: 0.5, y: 6.55, w: 7.6, h: 0.7,
    fontFace: FONT_TITLE, fontSize: 15, bold: true,
    color: COLORS.deepSpace, align: "left", valign: "middle",
  });
}

function addSvgImage(slide, pngAbsolutePath, x, y, w, h) {
  slide.addImage({ path: pngAbsolutePath, x, y, w, h });
}

function addSpeakerNote(slide, noteText) {
  try {
    slide.addNotes(noteText);
  } catch (e) {
    // Speaker notes may be unstable on some pptxgenjs versions; the master
    // copy of the speech is in notes/speaker_notes.md anyway.
  }
}

// Tiny helper: page number badge
function addPageNumber(slide, n, total = 12) {
  slide.addShape("ellipse", {
    x: 12.7, y: 0.05, w: 0.55, h: 0.55,
    fill: { color: COLORS.coralRed },
    line: { color: COLORS.cloudWhite, width: 2 },
  });
  slide.addText(`${n}/${total}`, {
    x: 12.7, y: 0.05, w: 0.55, h: 0.55,
    fontFace: FONT_TITLE, fontSize: 11, bold: true,
    color: COLORS.cloudWhite, align: "center", valign: "middle",
  });
}

// ---------------------------------------------------------------------------
// Main: build the deck
// ---------------------------------------------------------------------------
async function build() {
  const assetMap = await prepareAssets();
  const A = (svgName) => assetMap[svgName];

  const pres = new PptxGenJS();
  pres.layout = "LAYOUT_WIDE";
  pres.title = "科幻小说大冒险";
  pres.author = "Grade 6 Student";
  pres.company = "Class Sharing";
  pres.subject = "Science Fiction Adventure";

  // -------------------------------------------------------------------------
  // SLIDE 1 — Cover
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "deep");

    s.addText("科幻小说大冒险", {
      x: 0.5, y: 1.2, w: 12.3, h: 1.5,
      fontFace: FONT_TITLE, fontSize: 60, bold: true,
      color: COLORS.warmYellow, align: "center", valign: "middle",
      shadow: { type: "outer", color: "000000", blur: 6, offset: 3, angle: 45, opacity: 0.5 },
    });
    s.addText("种类  ·  结构  ·  有趣的科学设定", {
      x: 0.5, y: 2.8, w: 12.3, h: 0.6,
      fontFace: FONT_BODY, fontSize: 24,
      color: COLORS.cloudWhite, align: "center",
    });

    addSvgImage(s, A("rocket.svg"),     1.0, 3.6, 2.4, 2.8);
    addSvgImage(s, A("planet.svg"),     5.5, 4.0, 2.5, 2.5);
    addSvgImage(s, A("robot.svg"),     10.0, 3.7, 2.4, 2.8);

    // big speech bubble in the middle
    addSpeechBubble(s, "准备好了吗？  一起出发！", 4.0, 4.4, 5.3, 1.2);

    addMemoryPoint(s, "今天我们要进入科幻世界。");
    addPageNumber(s, 1);

    addSpeakerNote(s,
      "同学们好！今天我们要进入科幻小说的世界，学习三个核心秘密：" +
      "它有哪些种类？故事是怎么搭建的？还有那些让人拍大腿的有趣科学设定。" +
      "准备好了吗？出发！\n[预计时间：40 秒]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 2 — Opening interaction
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "这是童话，还是科幻？");

    addSvgImage(s, A("talking_bag.svg"), 0.8, 2.2, 3.6, 3.6);
    addSpeechBubble(s, "我会说话哦！", 4.6, 2.0, 3.4, 1.0);

    // Two compare cards
    addStepCard(s, "如果没有原因",
      "  •  像童话\n  •  魔法直接发生\n  •  不需要解释",
      4.6, 3.3, 3.9, 2.6, COLORS.coralRed);
    addStepCard(s, "如果装了 AI 芯片",
      "  •  像科幻\n  •  有科学解释\n  •  听起来像真的",
      8.7, 3.3, 4.2, 2.6, COLORS.techCyan);

    // big question sticker
    addSticker(s, "?", 4.0, 1.9, 0.6, 0.6, COLORS.warmYellow);

    addMemoryPoint(s, "科幻要有一个“看起来像真的理由”。");
    addInteractionBadge(s, "请举手投票");
    addPageNumber(s, 2);

    addSpeakerNote(s,
      "我先问大家一个问题：如果有一天，你的书包突然会说话，这算童话还是科幻？" +
      "觉得是童话的举手，觉得是科幻的举手。" +
      "其实关键不在于书包会不会说话，而在于有没有科学解释。" +
      "如果它只是突然说话，那更像童话；如果它里面装了 AI 芯片，那就更像科幻。\n[预计时间：1 分钟]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 3 — What is sci-fi
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "科学 + 幻想 = 科幻");

    // Magic cloud (童话)
    addStepCard(s, "童话",
      "神奇\n但不用解释\n魔杖一点 → 南瓜变马车",
      0.7, 2.2, 3.8, 3.4, COLORS.coralRed);

    // Equals
    s.addText("+", {
      x: 4.5, y: 3.4, w: 0.8, h: 1.0,
      fontFace: FONT_TITLE, fontSize: 60, bold: true,
      color: COLORS.deepSpace, align: "center", valign: "middle",
    });

    // Sci card (科幻)
    addStepCard(s, "科幻",
      "神奇\n但要有理由\n用科学解释幻想",
      5.4, 2.2, 3.8, 3.4, COLORS.techCyan);

    s.addText("=", {
      x: 9.2, y: 3.4, w: 0.6, h: 1.0,
      fontFace: FONT_TITLE, fontSize: 60, bold: true,
      color: COLORS.deepSpace, align: "center", valign: "middle",
    });

    // Result
    addStepCard(s, "结果",
      "让不可能\n听起来\n像可能",
      9.8, 2.2, 3.2, 3.4, COLORS.warmYellow);

    addMemoryPoint(s, "让不可能听起来像可能。");
    addPageNumber(s, 3);

    addSpeakerNote(s,
      "科幻和童话最大的区别是什么？童话里魔杖一点，南瓜变马车，不需要理由。" +
      "但科幻里，如果有人能瞬间移动，你一定得告诉我原因。" +
      "科幻就是：用科学来解释幻想，让假的事情听起来像真的一样。\n[预计时间：1 分钟]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 4 — Three kinds of sci-fi
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "科幻小说的三种类型");

    addStepCard(s, "硬科幻 · 硬糖",
      "科学很多，嚼劲十足\n讲原理，讲推导\n例如《流浪地球》",
      0.6, 2.0, 4.0, 3.6, COLORS.techCyan);
    addStepCard(s, "软科幻 · 棉花糖",
      "更重感情，软软的\n讲人和情感\n例如《你一生的故事》",
      4.7, 2.0, 4.0, 3.6, COLORS.coralRed);
    addStepCard(s, "幽默科幻 · 跳跳糖",
      "短小，惊喜不断\n常是脑洞小故事\n例如《喂——出来》",
      8.8, 2.0, 4.0, 3.6, COLORS.warmYellow);

    addMemoryPoint(s, "不同科幻，味道不一样。");
    addInteractionBadge(s, "你最想读哪一种？");
    addPageNumber(s, 4);

    addSpeakerNote(s,
      "科幻主要分三种。第一种是硬科幻，像硬糖一样有嚼劲，里面科学知识很多，比如《流浪地球》。" +
      "第二种是软科幻，像棉花糖，更关心人的感情，比如《你一生的故事》。" +
      "第三种是幽默科幻，像跳跳糖，短小又让人惊喜，比如星新一的《喂——出来》。" +
      "如果让你选，你最想读哪一种？\n[预计时间：1 分 20 秒]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 5 — Core formula
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "科幻故事的秘密公式");

    // big formula banner
    s.addShape("roundRect", {
      x: 0.6, y: 1.8, w: 12.1, h: 1.2,
      fill: { color: COLORS.starPurple },
      line: { color: COLORS.deepSpace, width: 3 },
      rectRadius: 0.2,
    });
    s.addText("如果……  会怎样……  那人怎么办？", {
      x: 0.6, y: 1.8, w: 12.1, h: 1.2,
      fontFace: FONT_TITLE, fontSize: 32, bold: true,
      color: COLORS.warmYellow, align: "center", valign: "middle",
    });

    // 3-step flow
    addStepCard(s, "1. 设定",
      "出现一个\n不可能的东西\n（科学小幻想）",
      0.7, 3.3, 3.8, 2.5, COLORS.techCyan);

    // arrow 1
    s.addShape("rightTriangle", {
      x: 4.6, y: 4.2, w: 0.5, h: 0.7,
      fill: { color: COLORS.coralRed }, line: { color: COLORS.deepSpace, width: 2 },
      rotate: 90,
    });

    addStepCard(s, "2. 推演",
      "它会带来\n什么后果？\n世界会怎么变？",
      5.2, 3.3, 3.8, 2.5, COLORS.warmYellow);

    s.addShape("rightTriangle", {
      x: 9.1, y: 4.2, w: 0.5, h: 0.7,
      fill: { color: COLORS.coralRed }, line: { color: COLORS.deepSpace, width: 2 },
      rotate: 90,
    });

    addStepCard(s, "3. 选择",
      "人在新世界里\n会怎么办？\n做出什么决定？",
      9.7, 3.3, 3.4, 2.5, COLORS.brightGreen);

    addMemoryPoint(s, "这是整场分享最重要的一页。");
    addPageNumber(s, 5);

    addSpeakerNote(s,
      "科幻小说和普通故事最大的不同，是它有一个特别清楚的结构。" +
      "我把它总结成三步：第一步，设定，先出现一个现实中不存在的东西；" +
      "第二步，推演，想一想它会带来什么后果；" +
      "第三步，选择，人在这个新世界里会怎么办。" +
      "简单说就是：如果……会怎样……那人怎么办？\n[预计时间：1 分 20 秒]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 6 — Three-Body case study
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "一个小设定，改变整个世界");

    addStepCard(s, "设定",
      "智子干扰\n科学实验\n（像超级计算机）",
      0.6, 2.0, 4.0, 3.0, COLORS.techCyan);

    addStepCard(s, "推演",
      "实验总是出错\n地球科技停滞\n人类陷入危机",
      4.7, 2.0, 4.0, 3.0, COLORS.warmYellow);

    addStepCard(s, "选择",
      "有人绝望\n有人反抗\n有人继续坚持",
      8.8, 2.0, 4.0, 3.0, COLORS.brightGreen);

    // small comic strip arrows
    s.addShape("rightTriangle", {
      x: 4.6, y: 3.2, w: 0.5, h: 0.7,
      fill: { color: COLORS.coralRed }, line: { color: COLORS.deepSpace, width: 2 },
      rotate: 90,
    });
    s.addShape("rightTriangle", {
      x: 8.7, y: 3.2, w: 0.5, h: 0.7,
      fill: { color: COLORS.coralRed }, line: { color: COLORS.deepSpace, width: 2 },
      rotate: 90,
    });

    // bottom example badge
    s.addShape("roundRect", {
      x: 0.6, y: 5.3, w: 12.2, h: 1.0,
      fill: { color: COLORS.starPurple },
      line: { color: COLORS.deepSpace, width: 2 },
      rectRadius: 0.15,
    });
    s.addText("案例 ·《三体》：从一个小粒子开始的大故事", {
      x: 0.6, y: 5.3, w: 12.2, h: 1.0,
      fontFace: FONT_TITLE, fontSize: 22, bold: true,
      color: COLORS.cloudWhite, align: "center", valign: "middle",
    });

    addMemoryPoint(s, "一个小设定，也能推开大故事。");
    addPageNumber(s, 6);

    addSpeakerNote(s,
      "比如《三体》里有一个设定叫“智子”。它只有一个质子那么大，却像超级计算机一样，" +
      "可以干扰地球科学实验。那会怎样？科学家做实验总是得不到正确结果，科技就很难继续进步。" +
      "那人类怎么办？有人绝望，但也有人选择反抗。你看，一个小设定，就能改变整个故事世界。\n[预计时间：1 分 20 秒]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 7 — Vote: which sci-fi prop?
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "如果只能选一个科幻道具，你选哪个？");

    // Four cards 2x2
    const cards = [
      { x: 0.6, y: 1.8, label: "A 记忆云盘", desc: "把不想要的\n记忆存进 U 盘", icon: "memory_disk.svg",     color: COLORS.techCyan   },
      { x: 7.0, y: 1.8, label: "B 情绪毛衣", desc: "穿上后感受\n别人的真实情绪", icon: "emotion_sweater.svg", color: COLORS.coralRed   },
      { x: 0.6, y: 4.3, label: "C 1%速度按钮", desc: "全世界变慢\n100 倍",          icon: "speed_button.svg",   color: COLORS.warmYellow },
      { x: 7.0, y: 4.3, label: "D 共享梦境 App", desc: "全班一起做\n同一个梦",       icon: "dream_app.svg",      color: COLORS.brightGreen},
    ];

    cards.forEach(c => {
      // shadow
      s.addShape("roundRect", {
        x: c.x + 0.08, y: c.y + 0.08, w: 5.7, h: 2.3,
        fill: { color: COLORS.deepSpace, transparency: 70 },
        line: { color: COLORS.deepSpace, transparency: 100 },
        rectRadius: 0.2,
      });
      // body
      s.addShape("roundRect", {
        x: c.x, y: c.y, w: 5.7, h: 2.3,
        fill: { color: COLORS.cloudWhite },
        line: { color: COLORS.deepSpace, width: 3 },
        rectRadius: 0.2,
      });
      // header strip
      s.addShape("roundRect", {
        x: c.x, y: c.y, w: 5.7, h: 0.6,
        fill: { color: c.color },
        line: { color: COLORS.deepSpace, width: 3 },
        rectRadius: 0.2,
      });
      s.addText(c.label, {
        x: c.x, y: c.y, w: 5.7, h: 0.6,
        fontFace: FONT_TITLE, fontSize: 18, bold: true,
        color: COLORS.deepSpace, align: "center", valign: "middle",
      });
      addSvgImage(s, A(c.icon), c.x + 0.25, c.y + 0.75, 1.5, 1.4);
      s.addText(c.desc, {
        x: c.x + 1.9, y: c.y + 0.75, w: 3.6, h: 1.4,
        fontFace: FONT_BODY, fontSize: 16,
        color: COLORS.deepSpace, align: "left", valign: "middle",
      });
    });

    addMemoryPoint(s, "好设定不只是好玩，还会带来麻烦。");
    addInteractionBadge(s, "请举手投票！");
    addPageNumber(s, 7);

    addSpeakerNote(s,
      "现在打开你们的脑洞！如果只能选一个科幻道具带回家，你会选哪一个？" +
      "A 记忆云盘，可以把不想要的记忆存进 U 盘；" +
      "B 情绪毛衣，穿上后能感受到别人的真实情绪；" +
      "C 1%速度按钮，按下后全世界变慢 100 倍；" +
      "D 共享梦境 App，全班做同一个梦。" +
      "现在请大家举手投票。投完后我们要想一想：它不只是好玩，还可能带来什么麻烦？" +
      "\n[预计时间：1 分 30 秒]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 8 — Build a story together
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "全班一起造一个科幻故事");

    addStepCard(s, "第 1 步",
      "这个道具\n出现了\n（用刚才得票最高的）",
      0.6, 2.0, 4.0, 3.4, COLORS.techCyan);
    addStepCard(s, "第 2 步",
      "它改变了\n什么？\n带来了什么麻烦？",
      4.7, 2.0, 4.0, 3.4, COLORS.warmYellow);
    addStepCard(s, "第 3 步",
      "主人公\n怎么选择？\n做出什么决定？",
      8.8, 2.0, 4.0, 3.4, COLORS.brightGreen);

    addSvgImage(s, A("rocket.svg"), 11.6, 5.4, 0.9, 1.1);

    s.addText("✏  请同学只说 1 个词或 1 句话", {
      x: 0.6, y: 5.6, w: 8.0, h: 0.6,
      fontFace: FONT_BODY, fontSize: 18, bold: true, italic: true,
      color: COLORS.coralRed, align: "left",
    });

    addMemoryPoint(s, "我们也能用三步法写科幻。");
    addInteractionBadge(s, "你来填一格");
    addPageNumber(s, 8);

    addSpeakerNote(s,
      "现在我们用刚才得票最高的道具，现场造一个小科幻故事。" +
      "第一步，这个道具出现了。第二步，它改变了什么，或者带来了什么麻烦？大家可以说一个词。" +
      "第三步，主人公要怎么选择？" +
      "你们发现没有，我们已经在用“设定、推演、选择”写故事了。" +
      "\n冷场备用：大家的脑洞很多，我们先收回来。记住重点：设定、推演、选择。" +
      "\n[预计时间：1 分 30 秒]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 9 — Three story breakdowns
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "用三步结构看懂科幻故事");

    const stories = [
      {
        x: 0.5, color: COLORS.techCyan, title: "《火星救援》",
        body: "设定：宇航员留在火星\n推演：造水，种土豆\n选择：用科学活下来",
      },
      {
        x: 4.7, color: COLORS.warmYellow, title: "《喂——出来》",
        body: "设定：发现无底洞\n推演：人们疯狂倒垃圾\n选择：逃避问题，被自然还回来",
      },
      {
        x: 8.9, color: COLORS.brightGreen, title: "《呼吸》",
        body: "设定：呼吸消耗生命\n推演：活着就是倒计时\n选择：接受真相，珍惜呼吸",
      },
    ];

    stories.forEach(st => {
      addStepCard(s, st.title, st.body, st.x, 2.0, 3.9, 4.0, st.color);
    });

    addMemoryPoint(s, "再复杂的科幻，也能先用三步看懂。");
    addPageNumber(s, 9);

    addSpeakerNote(s,
      "我们再用这个方法看三个故事。" +
      "《火星救援》里，一个宇航员被落在火星上，他没有等死，而是用科学办法造水、种土豆，最后活下来。" +
      "《喂——出来》里，人们发现一个无底洞，以为垃圾永远不会回来，就疯狂往里面扔，结果最后垃圾从天上掉回来了。" +
      "《呼吸》里，机器人每呼吸一次，就在消耗生命，但它选择接受真相，珍惜每一次呼吸。" +
      "三个故事都不一样，但结构都是：设定、推演、选择。" +
      "\n[预计时间：2 分钟]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 10 — Sci-fi becoming reality
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "科幻正在变成现实");

    // Brain interface card
    const x1 = 0.6, x2 = 4.7, x3 = 8.8;
    addStepCard(s, "脑机接口",
      "用念头\n控制设备\n打字 / 玩游戏",
      x1, 2.0, 4.0, 3.6, COLORS.techCyan);
    addSvgImage(s, A("brain_interface.svg"), x1 + 0.5, 4.0, 1.4, 1.4);

    addStepCard(s, "太空电梯",
      "坐电梯\n去太空\n不再靠火箭",
      x2, 2.0, 4.0, 3.6, COLORS.warmYellow);
    addSvgImage(s, A("rocket.svg"), x2 + 0.5, 4.0, 1.4, 1.4);

    addStepCard(s, "人造光合作用",
      "材料像\n树叶一样\n用阳光发电",
      x3, 2.0, 4.0, 3.6, COLORS.brightGreen);
    addSvgImage(s, A("planet.svg"), x3 + 0.5, 4.0, 1.4, 1.4);

    addMemoryPoint(s, "科幻是提前到来的未来。");
    addPageNumber(s, 10);

    addSpeakerNote(s,
      "很多科幻里的东西，正在慢慢变成真的。比如脑机接口，听起来像用念头打字；" +
      "太空电梯，听起来像坐电梯上太空；" +
      "人造光合作用，听起来像让材料像树叶一样利用阳光。" +
      "科幻不是胡思乱想，它有时候是在提前想象未来。" +
      "\n[预计时间：1 分钟]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 11 — We can write sci-fi
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "light");
    addTitle(s, "写科幻的万能公式");

    // Template card
    s.addShape("roundRect", {
      x: 0.6, y: 1.9, w: 9.0, h: 4.4,
      fill: { color: COLORS.cloudWhite },
      line: { color: COLORS.deepSpace, width: 3 },
      rectRadius: 0.2,
    });

    const lines = [
      { y: 2.1, text: "如果有一天，____________________ 出现了。" },
      { y: 3.1, text: "一开始，它让大家 ____________________。" },
      { y: 4.1, text: "可是后来，____________________________。" },
      { y: 5.1, text: "最后，主人公选择 ___________________。" },
    ];
    lines.forEach((l, i) => {
      // small dot index
      s.addShape("ellipse", {
        x: 0.85, y: l.y + 0.15, w: 0.45, h: 0.45,
        fill: { color: [COLORS.techCyan, COLORS.warmYellow, COLORS.coralRed, COLORS.brightGreen][i] },
        line: { color: COLORS.deepSpace, width: 2 },
      });
      s.addText(`${i + 1}`, {
        x: 0.85, y: l.y + 0.15, w: 0.45, h: 0.45,
        fontFace: FONT_TITLE, fontSize: 14, bold: true,
        color: COLORS.deepSpace, align: "center", valign: "middle",
      });
      s.addText(l.text, {
        x: 1.5, y: l.y, w: 8.0, h: 0.7,
        fontFace: FONT_BODY, fontSize: 20, bold: true,
        color: COLORS.deepSpace, align: "left", valign: "middle",
      });
    });

    addSvgImage(s, A("rocket.svg"), 10.0, 2.0, 2.6, 3.0);
    addSvgImage(s, A("story_formula.svg"), 9.7, 5.1, 3.2, 1.3);

    addMemoryPoint(s, "先问“如果”，故事就开始了。");
    addPageNumber(s, 11);

    addSpeakerNote(s,
      "其实我们也可以写科幻。你只要套这个公式：" +
      "如果有一天，某个神奇科技出现了；一开始，它让大家怎么样；" +
      "可是后来，它带来了什么麻烦；最后，主人公做出了什么选择。" +
      "这样，一个科幻故事就有了。" +
      "\n[预计时间：1 分钟]");
  }

  // -------------------------------------------------------------------------
  // SLIDE 12 — Closing
  // -------------------------------------------------------------------------
  {
    const s = pres.addSlide();
    addStarBackground(s, "purple");

    s.addText("插上你的科幻翅膀", {
      x: 0.5, y: 0.6, w: 12.3, h: 1.2,
      fontFace: FONT_TITLE, fontSize: 48, bold: true,
      color: COLORS.warmYellow, align: "center", valign: "middle",
      shadow: { type: "outer", color: "000000", blur: 6, offset: 3, angle: 45, opacity: 0.5 },
    });

    // Big quote card
    s.addShape("roundRect", {
      x: 1.0, y: 2.0, w: 11.3, h: 2.7,
      fill: { color: COLORS.cloudWhite },
      line: { color: COLORS.warmYellow, width: 4 },
      rectRadius: 0.25,
    });
    s.addText(
      "每一个大科学家小时候，\n都是先成为大幻想家。\n\n你的科幻翅膀，就藏在每天问的那个：\n“如果……会怎样？”",
      {
        x: 1.2, y: 2.1, w: 10.9, h: 2.5,
        fontFace: FONT_BODY, fontSize: 22, bold: true,
        color: COLORS.deepSpace, align: "center", valign: "middle",
        paraSpaceAfter: 4,
      }
    );

    addSvgImage(s, A("robot.svg"),  0.8, 4.9, 1.7, 2.0);
    addSvgImage(s, A("rocket.svg"), 5.7, 4.9, 1.5, 2.0);
    addSvgImage(s, A("planet.svg"),10.8, 4.9, 1.7, 1.7);

    s.addText("谢 谢 大 家！", {
      x: 3.0, y: 5.4, w: 7.5, h: 0.8,
      fontFace: FONT_TITLE, fontSize: 30, bold: true,
      color: COLORS.warmYellow, align: "center", valign: "middle",
    });

    addMemoryPoint(s, "保持好奇，就是科幻的开始。");
    addPageNumber(s, 12);

    addSpeakerNote(s,
      "每一个大科学家小时候，都是先成为大幻想家。" +
      "你的科幻翅膀，就藏在每天问的那个“如果……会怎样？”里。" +
      "我的分享结束，谢谢大家！" +
      "\n[预计时间：40 秒]");
  }

  // -------------------------------------------------------------------------
  // Save
  // -------------------------------------------------------------------------
  const outDir  = path.join(__dirname, "output");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, "science_fiction_adventure_grade6.pptx");
  await pres.writeFile({ fileName: outFile });
  console.log("[OK] PPTX generated at:", outFile);
  return outFile;
}

build().catch(err => {
  console.error("[ERROR] Build failed:", err);
  process.exit(1);
});
