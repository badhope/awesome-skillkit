# Frontend design

> 这个文件不是给 AI 看的"产品规格"，是给前端开发者 / 设计师
> 看的设计 brief。我们想要做出来的东西跟 GitHub 默认的
> awesome-list 长得不一样，但也不装作"Apple 风的 marketing
> page"。就是一个**给程序员用的站点**。

## 一句话

GitHub Pages 静态站，浏览本地技能。**没有营销腔**，
没有 "Sign up"，没有 carousel，没有 stats counter，
没有 hero section 配一张抽象的 3D 图。

就是：列表 → 点开 → 读完 → 装上。

## 调性

参考这几个东西的"形"（不是颜色）：

- **Vercel docs** —— 字号层级清楚，密度高但不挤
- **Stripe API reference** —— 代码块 + 文字混排的节奏
- **Tailwind UI 的 "Simple" 主题** —— 但不要它那个灰底色
- **Linear 的 changelog 页** —— 列表密度，干净分割
- **Tailscale 的 landing page** —— 一句话讲清，不堆修饰

**不是**：Medium、Notion、Substack。**也不是**：
Vercel 营销页那种 hero + 数字 + 大图。

## 配色

不用色板。**用 token**：

```css
:root {
  /* surface */
  --bg:        #fafaf7;   /* 暖白，不是纯白 #fff */
  --bg-elev:   #ffffff;
  --bg-sunk:   #f1efe9;
  --border:    #e5e2d8;   /* 同色系，比底色再深一点 */
  --border-strong: #2a2a2a;

  /* text */
  --ink:       #1a1a1a;
  --ink-soft:  #4a4a48;
  --ink-mute:  #888580;

  /* accent */
  --accent:    #2a2a2a;   /* 几乎就是黑 */
  --accent-fg: #fafaf7;

  /* 状态色：克制 */
  --ok:        #2d6a4f;   /* 深绿，不要 emerald-500 */
  --warn:      #b45309;   /* 琥珀 */
  --err:       #991b1b;   /* 深红 */
  --info:      #1d4ed8;   /* 深蓝 */

  /* 平台标签颜色：固定，按平台 */
  --p-claude:  #c96442;   /* Claude 橙 */
  --p-codex:   #10a37f;   /* OpenAI 绿 */
  --p-cursor:  #000000;
  --p-continue:#5b6cff;
}
```

**原则**：

- 默认走 light theme
- dark mode 跟 light 用**同一套 token**反过来 —— `prefers-color-scheme` 自动切，不要按钮
- 不用渐变，不用 shadow 卡片的"漂浮感"
- 不用任何 Tailwind 默认色（`blue-500` 那个蓝）
- 状态色只在真的需要的时候用（错误、警告、needs-review 标记）

## 字体

- **正文 / UI**: `Inter` 兜底，本地不要引 Google Fonts（CDN 在某些地区慢）
  - 自托管 `Inter-Variable.woff2`
  - 子集化到拉丁 + 拉丁扩展 + CJK
- **代码 / frontmatter / prompt**: `JetBrains Mono`
  - 同样自托管
- **不要**用花哨的 display font。**不要**用衬线
- 字号：14px / 16px / 18px / 22px / 28px / 40px，就这 6 档
- 行高：正文 1.6，代码 1.5，标题 1.25
- 字符宽度：英文 ~70ch 一行代码块舒服

## 间距 & 布局

8px 网格，全站只用 `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64` 这 8 个值。
不要 13px、17px 这种半吊子。

容器宽度：

- `max-width: 72rem` (1152px) —— 列表页主区
- `max-width: 56rem` (896px)  —— 详情页正文
- `max-width: 100%` 减去 padding —— 移动端

## 三个页面

### 1. `/` — 列表页

```
┌──────────────────────────────────────────┐
│  AI-SKILL                      [GitHub]  │  ← top bar, 56px
├──────────────────────────────────────────┤
│  N skills · 49 categories · 0 to review │  ← meta line
├──────────────────────────────────────────┤
│  [search]  [category ▾]  [platform ▾]    │  ← filter bar
├──────────────────────────────────────────┤
│  ┌────────────────────────────────────┐  │
│  │ pdf-summarizer                     │  │
│  │ 给 PDF 出 N 条 bullet 摘要         │  │  ← skill card
│  │ document-processing · [claude]     │  │
│  │ ─────────────                       │  │
│  │ inputs: pdf_path, audience         │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ url-extractor                      │  │
│  │ ...                                │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

**卡片细节**：

- 整张卡可点
- 卡片之间 8px 间距，不要框线。要分割感就用 bg 颜色交替（white / sunk）
- 鼠标 hover：左边出 2px 实心 border-left（accent 色），背景不变
- 触摸：tap 即点，**无 hover 效果**
- 平台 tag 是小 chip，固定色（看上面 `--p-*`），不写文字直接给色块 + tooltip
- `needs_review: true` 的卡片右上角一个小圆点，**`var(--warn)`**，不喧宾夺主
- 移动端：单列，卡片变紧凑，meta 在卡片底部

### 2. `/skill/<slug>` — 详情页

布局：

```
┌──────────────────────────────────────────┐
│  ← back                                   │
├──────────────────────────────────────────┤
│  pdf-summarizer                          │  ← H1, 40px
│  PDF Summarizer · v0.1.0 · MIT           │  ← meta
│  document-processing · [claude]          │  ← tags
├──────────────────────────────────────────┤
│  When to use  (anchored, 22px)            │
│  ...                                       │
│                                            │
│  Inputs                                    │
│  ┌────────────────────────────────────┐  │  ← table
│  │ pdf_path    path     required     │  │
│  │ audience    enum     optional     │  │
│  │ ...                                │  │
│  └────────────────────────────────────┘  │
│                                            │
│  Output                                    │
│  ...                                       │
│                                            │
│  Prompt                                    │
│  ┌────────────────────────────────────┐  │  ← code block
│  │ You are a senior analyst...        │  │
│  │ ...                                │  │
│  └────────────────────────────────────┘  │
│  [Copy] [Download .md] [Install ▾]      │  ← actions
│                                            │
│  When NOT to use                           │
│  ...                                       │
│                                            │
│  Example                                   │
│  ...                                       │
└──────────────────────────────────────────┘
```

**关键交互**：

- **Copy** 按钮：复制 prompt 整段，复制成功后 1.5s 内按钮文字变 "Copied"
- **Download .md**：触发 `SKILL.md` 文件下载
- **Install ▾**：下拉菜单，"Copy to Claude (~/.claude/skills)" / "Copy to Codex" / "Copy to..." 自定义路径。点击 → 走 `install-skill.py` 思路（前端用 JS 模拟 + File System Access API，或者直接下载让用户手动复制）。**v1 不做完整安装，只给下载**，不骗人
- TOC 在右侧 sticky，仅桌面端，移动端折到顶部
- 代码块带**复制**小按钮（右上角）
- 锚点跳转带平滑滚动，hash 更新

### 3. `/bundle` — 批量下载

```
┌──────────────────────────────────────────┐
│  Pick skills, get a ZIP                   │
├──────────────────────────────────────────┤
│  [select all] [clear] [filter...]         │
│  ☐ pdf-summarizer     document-processing │
│  ☐ url-extractor      web                 │
│  ☐ ...                                   │
├──────────────────────────────────────────┤
│  Selected: 3 skills                       │
│  [Download .zip]                          │
└──────────────────────────────────────────┘
```

**实现思路**：

- v1：纯前端，用 `JSZip` 把多个 SKILL.md 打包
- 不调后端
- 下载文件名：`ai-skill-<n-skills>-<yyyymmdd>.zip`

## 移动端

**断点**：`< 768px` 一律单列，`< 480px` 字号小一档。

**几个易踩的坑**：

- 顶部 nav 不能 `position: fixed` 抢屏幕 —— 用 `sticky` 且 56px 高
- 搜索框要全宽，按钮放搜索框下面
- 详情页 TOC 隐藏，内容自己滚
- 代码块横向滚动条**永远显示**（不要 `overflow: hidden`），拖动顺畅
- tap target 至少 44×44px
- 字体不要锁 `min-font-size`，让 iOS Safari 自己决定
- 卡片不要用 1px border 区分 hover —— 用背景色差

## 动效

**全部 ≤ 200ms。** 不要 spring，不要 bounce。

- hover transition: `background-color 120ms`, `border-color 120ms`, `transform 150ms`
- 复制成功的 feedback：scale(1) → scale(1.04) → scale(1)，150ms
- 页面切换：fade in 100ms，不要 slide
- 滚动：用 `scroll-behavior: smooth`，但 hash 跳转给个 `prefers-reduced-motion` 兜底

**不准用**：

- 视差滚动
- 鼠标跟随效果
- 鼠标光标自定义
- 数字滚动动画（counter 那种）
- Lottie
- 任何 Lottie-like 的"装饰性"动画

## Icon

**不用 icon library**。**不用 emoji**。最多 3 个内联 SVG：

- back arrow
- copy
- download

其他全部用文字。tag 是文字 + 颜色块，不是 icon。

## 性能预算

- LCP < 1s
- CLS = 0
- 总 JS < 50KB gzipped（vanilla TS，no framework）
- 总 CSS < 20KB gzipped
- 一张图都不引（如果要 logo 就 inline SVG）

## 不要做的事（最后强调一遍）

- ❌ "Get started" 大按钮
- ❌ "Trusted by 10,000+ developers"
- ❌ 3D 抽象图 / 渐变 mesh
- ❌ Tailwind 默认色（slate-、blue-、emerald-）
- ❌ 任何 "AI" 字样出现在 UI 上 —— 仓库是 AI-SKILL，
  不代表网页要写"AI-powered" 那种废话
- ❌ "Subscribe to newsletter" 弹窗
- ❌ cookie consent banner（GitHub Pages 静态站，不放第三方脚本）
- ❌ 视频 / gif demo（要么静态截图，要么没）

---

## 给实现者的几个 takeaway

1. 先把 **列表页**做到能看，其它两个页面**复用**它
2. 配色和字体先定，剩下都是盒子
3. 移动端**一开始**就同时做，不要"先做桌面再加 mobile"
4. 唯一允许的第三方库：`JSZip`（bundle 页面用）。其他自己写
5. 写完之后 dev 面板把 throttling 拨到 "Slow 3G" 自己看一次
6. 把 `prefers-reduced-motion` 测一遍
