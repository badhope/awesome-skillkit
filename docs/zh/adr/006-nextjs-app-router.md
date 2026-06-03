# ADR 006 — Next.js 15 App Router

- **状态**：已采纳
- **日期**：2026-06-01

## 背景

前端是一个面向公网的技能浏览器。它需要 SEO、Streaming、Server Components，以及一套成熟的国际化方案。

## 决策

使用 **Next.js 15 + App Router** 与 React 19。

## 依据

- Server Components 让我们免去 "loader / suspense" 的样板代码。
- App Router 的基于文件的路由易于浏览。
- 内置 i18n 能力；为了更细的控制我们自实现了一套。
- 开箱即用支持 Edge / 静态渲染。

## 候选方案

| 方案            | 原因未选                                       |
|-----------------|-----------------------------------------------|
| Pages Router    | 旧式；无 RSC；社区已迁向 App Router           |
| Remix           | 优秀，但 UI 组件生态略小                      |
| Astro           | 内容站极佳；作为应用则偏弱                    |
| 原生 React + Vite | 没有 SEO 和 SSR，需要额外工作             |

## 后果

- 我们必须**节制**使用 `'use client'`；大多数页面是 RSC。
- 默认开启 streaming；搜索结果借助 `<Suspense>` 渲染。
- 避免只在 client 跑的库（比如导入时即访问 `window` 的库）。
