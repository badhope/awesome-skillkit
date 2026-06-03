# 新增一个前端页面

前端使用 Next.js 15 **App Router**。页面位于
`frontend/src/app/<route>/page.tsx`，文件系统即是路由表。

## 1. 决定 Server 还是 Client

默认情况下，App Router 中的文件是 **Server Component**。只有在以下
场景才在文件顶部添加 `'use client'`：

- 使用 `useState` / `useEffect` 等 React Hook
- 使用仅浏览器可用的 API（`window`、`localStorage`）
- 使用事件处理器（`onClick`、`onChange`）

大多数页面应保持 Server Component，仅在专门的 Client 组件中使用
TanStack Query。

## 2. 创建页面

```tsx
// frontend/src/app/skills/[slug]/history/page.tsx
import { SkillHistoryList } from '@/components/SkillHistoryList';

interface PageProps {
  params: { slug: string };
}

export default function Page({ params }: PageProps) {
  return <SkillHistoryList slug={params.slug} />;
}
```

## 3. Client 组件

```tsx
// frontend/src/components/SkillHistoryList.tsx
'use client';

import { useQuery } from '@tanstack/react-query';
import { useI18n } from '@/lib/i18n';

export function SkillHistoryList({ slug }: { slug: string }) {
  const { t } = useI18n();
  const { data, isPending, isError } = useQuery({
    queryKey: ['skill-history', slug],
    queryFn: () => fetch(`/api/v1/skills/${slug}/history`).then((r) => r.json()),
  });

  if (isPending) return <Skeleton />;
  if (isError) return <ErrorMessage message={t('errors.loading')} />;
  if (!data?.length) return <EmptyState message={t('history.empty')} />;

  return (
    <ul>
      {data.map((entry) => (
        <li key={entry.version}>
          <strong>{entry.version}</strong> · {entry.changelog}
        </li>
      ))}
    </ul>
  );
}
```

## 4. 翻译键

在 `frontend/src/lib/i18n/translations.ts` 中新增键：

```ts
export const en = {
  history: {
    empty: 'No history yet for this skill.',
  },
  errors: {
    loading: 'Could not load. Please try again.',
  },
};

export const zh = {
  history: {
    empty: '该技能暂无历史记录。',
  },
  errors: {
    loading: '加载失败，请重试。',
  },
};
```

## 5. Loading 与 Error 状态

App Router 提供了一些文件级约定：

- `loading.tsx` —— 页面渲染期间的 Suspense fallback
- `error.tsx` —— 错误边界
- `not-found.tsx` —— 404 页面

视情况在页面同级位置创建：

```
skills/[slug]/history/
├── page.tsx
├── loading.tsx
├── error.tsx
└── not-found.tsx
```

## 6. 测试

一个 React Testing Library 测试：

```tsx
// frontend/src/components/SkillHistoryList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SkillHistoryList } from './SkillHistoryList';

it('renders history entries', async () => {
  fetchMock.mockResponseOnce(JSON.stringify([
    { version: '1.0.0', changelog: 'Initial release', created_at: '…' },
  ]));
  const client = new QueryClient();
  render(
    <QueryClientProvider client={client}>
      <SkillHistoryList slug="react-usememo-deep-dive" />
    </QueryClientProvider>
  );
  await waitFor(() => screen.getByText('Initial release'));
});
```

## 7. 运行 Linter 与测试

```bash
make lint
make test-frontend
```

## 约定

- **默认 Server** —— 仅在必要时才用 `'use client'`。
- **样式就近** —— 与组件同目录，而不是放进全局 CSS。
- **每个用户可见字符串都要 i18n** —— 详见
  `frontend/src/lib/i18n/translations.ts`。
- **不要硬编码 URL** —— 使用 `frontend/src/lib/api.ts` 里的
  `apiBaseUrl()` 助手。
- **类型安全 props** —— 使用 TypeScript 接口，禁止 `any`。

## 接下来去哪里

- [新增一个 API 端点](adding-endpoint.md) —— 配套指南
- [测试](testing.md) —— 前端测试说明
