# Adding a frontend page

The frontend uses the Next.js 15 **App Router**. Pages live in
`frontend/src/app/<route>/page.tsx` and the file system is the
routing table.

## 1. Decide server vs. client

By default, files in the App Router are **server components**. Add
`'use client'` at the top of a file only when you need:

- `useState` / `useEffect` / other React hooks
- Browser-only APIs (`window`, `localStorage`)
- Event handlers (`onClick`, `onChange`)

Most pages should remain server components and use TanStack Query on
the **client** only inside dedicated client components.

## 2. Create the page

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

## 3. The client component

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

## 4. Translation key

Add a key to `frontend/src/lib/i18n/translations.ts`:

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

## 5. Loading and error states

The App Router has file-based conventions:

- `loading.tsx` — Suspense fallback while the page is rendering
- `error.tsx` — Error boundary
- `not-found.tsx` — 404 page

Place one of each near your new page if it makes sense:

```
skills/[slug]/history/
├── page.tsx
├── loading.tsx
├── error.tsx
└── not-found.tsx
```

## 6. Test

A React Testing Library test:

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

## 7. Run the linters and tests

```bash
make lint
make test-frontend
```

## Conventions

- **Server by default** — only use `'use client'` when you need to.
- **Co-locate styles** with the component, not in a global CSS
  file.
- **i18n every user-facing string** — see
  `frontend/src/lib/i18n/translations.ts`.
- **No hard-coded URLs** — use the `apiBaseUrl()` helper from
  `frontend/src/lib/api.ts`.
- **Type-safe props** — use TypeScript interfaces, never `any`.

## Where to go from here

- [Adding an API endpoint](adding-endpoint.md) — companion guide
- [Testing](testing.md) — frontend test setup
