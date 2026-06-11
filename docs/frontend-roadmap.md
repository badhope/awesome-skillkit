# Frontend roadmap — 把 vault 网站真做出来

> 状态：进行中（用户指出"前端网站好像也没构建好"，本文件做规划 + 落地清单）

## 现状（deltas）

`frontend/dist/` 已经存在，35 条技能 JSON 都已经切片。
`tsc --noEmit && vite build` 干净，dist 总大小 ~5 MB（含 35 个 JSON）。

**但"功能性存在"和"做得好"是两件事**。具体问题：

| 维度 | 现状 | 目标 |
|---|---|---|
| 入口体验 | 列表页直接铺卡片，没有 hero/intro | 有 hero、stats、"什么是这个项目" 解释 |
| 字体 | system 栈 | 自托管 / Google Fonts：Inter + JetBrains Mono |
| 列表页 | 35 张卡平铺，没分组 | 按 category 折叠分组，header 加 featured |
| 详情页 | 4 段正文 + TOC | 加上 source 归属（`vendor + commit + url`）、相关技能（同 category 3 条） |
| 404 | unknown slug → 空白 | 跳到有用的 "not found" 页，附搜索框 + 返回 |
| 动效 | 无 | 进场 stagger、hover 微动、focus ring、过渡 120ms |
| footer | 3 个字 | 加 GitHub / docs / license 链接 |
| Bundle 页 | 已经能用 | 不动 |

## 实现顺序（按价值排序）

### F1. 写 `index.html` 真实骨架
- `<head>` 加 Google Fonts preconnect / preload
- `<header>` 不动
- **新增**：`<section class="hero">` 区域（在 main 之前或作为 list 页头）
- `<noscript>` 提示保留
- `<footer>` 改丰富

### F2. `style.css` 重写设计 token + 组件
- 字体变量从 system 改成 Inter / JetBrains Mono
- 设计 token 保留 8px grid，加 `--t-display` / `--t-h1` 等级
- 配色微调：主色 `#ff5b1f`（橙）作为 accent，主背景 #fafaf7
- 加 `@keyframes` 进场动效
- 加 `:focus-visible` 全局 outline
- 加 `.hero`、`.stats`、`.skill-card` 重设计
- 暗色模式保留

### F3. `list.ts` 改造
- 顶部加 hero（标题 + 描述 + 3 个 stat 数字）
- 搜索框下面加 "Featured / All" 切换
- 卡片重设计：左侧色条（按 category 配色），右侧内容更紧
- 卡片底部加 mini-tags 横向
- 列表按 category 分组（折叠面板），方便扫读

### F4. `detail.ts` 加 source / related
- frontmatter 下面加 source 归属块（如果是抓来的，显示 vendor + commit + url + license）
- 文末加 "Related skills" 块：同 category 取 3 条
- meta-row 加 last-updated 日期

### F5. `main.ts` 加 404 处理
- 路由 `#/skill/<unknown>` → 渲染 not-found 页（不是空白）
- not-found 页有搜索框 + 返回列表按钮

### F6. 动效
- `@keyframes fadeUp`：opacity 0→1，translateY 8px→0
- 卡片用 `animation-delay: calc(var(--i) * 30ms)` 做 stagger
- hover 卡片有 `transform: translateY(-2px)` 和 box-shadow 加深
- 按钮 hover 有微反色

### F7. footer 改丰富
```
MIT · vendor-neutral · no tracking
[GitHub repo] · [SOURCE.md] · [CONTRIBUTING] · [License]
```

## 不做（避免 over-engineer）

- ❌ 引入 React / Vue / 任何运行时框架 —— vanilla TS 够
- ❌ 引入 marked.js 之类的 markdown 库 —— 自己渲染够用
- ❌ 引入 Tailwind / PostCSS —— 12 KB CSS 手写就行
- ❌ 国际化（i18n）—— 双语用 `name_zh` / `description_zh` 字段做
- ❌ 暗色模式切换按钮 —— `prefers-color-scheme` 自动
- ❌ 任何运行时数据获取（SSR / ISR）—— GitHub Pages 静态
- ❌ CDN 自定义字体（用 Google Fonts CDN 即可）

## 验收

1. `python3 scripts/validate-skill.py --strict skills/` 仍 0/0/0
2. `cd frontend && npm run build` 干净
3. `python3 -m http.server -d frontend/dist 8765` 启起来
4. 浏览器打开 `http://localhost:8765/`
   - 看到 hero 标题 + 描述 + stats
   - 看到 35 张卡片，按 category 分组
   - 点一张卡 → 详情页有 source 块和 related skills
   - 输入 `#/skill/nonexistent` → 看到 not-found 页
5. 暗色模式 `prefers-color-scheme: dark` 自动切
6. 移动端（窄屏）布局不破

## 不在范围

- 搜索性能优化（35 条不需要）
- 离线 PWA（Vite PWA plugin 太大）
- 全文搜索（fuse.js 没必要）
- 服务端 analytics（无服务器）
