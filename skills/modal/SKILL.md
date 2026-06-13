---
name: modal
name_zh: modal
description: LobeHub imperative modal conventions. Use when creating or 
  migrating modals, dialogs, popups, confirm flows, ModalHost wiring, 
  createModal, confirmModal, useModalContext, or base-ui modal APIs.
description_zh: LobeHub imperative modal conventions. Use when creating or 
  migrating modals, dialogs, popups, confirm flows, ModalHost wiring, 
  createModal, confirmModal, useModalContext, or base-ui modal APIs.
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - docker
source:
needs_review: false
slug: modal
version: 1.0.0
created: '2026-06-12'
updated: '2026-06-12'
inputs:
  - name: request
    type: string
    required: true
    description: User request or task description
output:
  format: markdown
  description: Generated content based on the user request
author: AI-SKILL
license: MIT
---
# When to use

Use this skill when you need guidance on modal.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Modal Imperative API Guide

## Recommended: `@lobehub/ui/base-ui`

New code should use the **base-ui** modal stack (headless primitives, not antd `Modal`):

- `createModal`, `confirmModal`, `ModalHost` from `@lobehub/ui/base-ui`
- `useModalContext` from `@lobehub/ui/base-ui` inside modal **content**

Body slot: pass **`content`** (or `children`; runtime uses `content ?? children`).

### Global `ModalHost` (required)

Base-ui `createModal` renders through a **separate** host from the root package. The app must mount **`ModalHost`** from `@lobehub/ui/base-ui` once near the root (e.g. next to other global hosts). Without it, `createModal` calls will not appear.

If the project only mounts `ModalHost` from `@lobehub/ui`, add a second lazy `ModalHost` from `@lobehub/ui/base-ui` until all imperative modals are migrated.

### Why imperative?

| Mode        | Characteristics                      | Recommended |
| ----------- | ------------------------------------ | ----------- |
| Declarative | `open` state + `<Modal />`           | ❌          |
| Imperative  | Call `createModal()`, no local state | ✅          |

### File structure

```
features/
└── MyFeatureModal/
    ├── index.tsx            # export createXxxModal
    └── MyFeatureContent.tsx # modal body
```

### 1. Content (`MyFeatureContent.tsx`)

```tsx
'use client';

import { useModalContext } from '@lobehub/ui/base-ui';
import { useTranslation } from 'react-i18next';

export const MyFeatureContent = () => {
  const { t } = useTranslation('namespace');
  const { close } = useModalContext();

  return <div>{/* ... */}</div>;
};
```

### 2. `createModal` (`index.tsx`)

```tsx
'use client';

import { createModal } from '@lobehub/ui/base-ui';
import { t } from 'i18next';

import { MyFeatureContent } from './MyFeatureContent';

export const createMyFeatureModal = () =>
  createModal({
    content: <MyFeatureContent />,
    footer: null,
    maskClosable: true,
    styles: {
      content: { overflow: 'hidden', padding: 0 },
    },
    title: t('myFeature.title', { ns: 'setting' }),
    width: 'min(80%, 800px)',
  });
```

### 3. Usage

```tsx
import { createMyFeatureModal } from '@/features/MyFeatureModal';

const handleOpen = useCallback(() => {
  createMyFeatureModal();
}, []);

return <Button onClick={handleOpen}>Open</Button>;
```

### i18n

- **Content**: `useTranslation` in components.
- **`createModal` options**: `import { t } from 'i18next'` where hooks are unavailable.

### `useModalContext`

```tsx
const { close, setCanDismissByClickOutside } = useModalContext();
```

### Common options (base-ui)

`ImperativeModalProps` builds on `BaseModalProps`: `title`, `width`, `maskClosable`, `open`, `onOpenChange`, `footer`, `styles` / `classNames` (keys: `backdrop`, `popup`, `header`, `title`, `close`, `content`, …).

| Property       | Notes                                    |
| -------------- | ---------------------------------------- |
| `content`      | Main body (preferred name vs `children`) |
| `maskClosable` | Click outside to dismiss                 |
| `styles.*`     | Semantic regions, not antd `styles.body` |

### Confirm

```tsx
import { confirmModal } from '@lobehub/ui/base-ui';

confirmModal({
  title: '…',
  content: '…',
  okText: '…',
  cancelText: '…',
  onOk: async () => {},
});
```

---

## Legacy: `@lobehub/ui` (root)

Older call sites use **`createModal` from `@lobehub/ui`**, which is typed as **antd `Modal` props** (`children`, `allowFullscreen`, `getContainer`, `destroyOnHidden`, `styles.body`, etc.). Prefer migrating new work to **`@lobehub/ui/base-ui`**.

Examples (legacy): `src/features/SkillStore/index.tsx`, `src/features/LibraryModal/CreateNew/index.tsx`.

---

## Examples

- Base-ui (preferred): follow sections above; ensure **base-ui `ModalHost`** is mounted.
- Legacy: `src/features/SkillStore/index.tsx`, `src/features/LibraryModal/CreateNew/index.tsx`

# Example

Complete modal implementation using base-ui:

```tsx
// features/UserProfileModal/UserProfileContent.tsx
'use client';

import { useModalContext } from '@lobehub/ui/base-ui';
import { useTranslation } from 'react-i18next';
import { Button, Input, Form } from '@lobehub/ui';

export const UserProfileContent = ({ userId }: { userId: string }) => {
  const { t } = useTranslation('user');
  const { close } = useModalContext();

  const handleSubmit = async (values: any) => {
    await updateUserProfile(userId, values);
    close();
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Item name="name" label={t('profile.name')}>
        <Input />
      </Form.Item>
      <Form.Item name="email" label={t('profile.email')}>
        <Input type="email" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit">
          {t('profile.save')}
        </Button>
      </Form.Item>
    </Form>
  );
};
```

```tsx
// features/UserProfileModal/index.tsx
'use client';

import { createModal } from '@lobehub/ui/base-ui';
import { t } from 'i18next';
import { UserProfileContent } from './UserProfileContent';

export const createUserProfileModal = (userId: string) =>
  createModal({
    content: <UserProfileContent userId={userId} />,
    title: t('user:profile.editTitle'),
    width: 'min(90%, 600px)',
    maskClosable: true,
  });
```

```tsx
// Usage in component
import { createUserProfileModal } from '@/features/UserProfileModal';

const UserList = () => {
  const handleEditProfile = (userId: string) => {
    createUserProfileModal(userId);
  };

  return (
    <Button onClick={() => handleEditProfile('user-123')}>
      Edit Profile
    </Button>
  );
};
```

# When NOT to use

Do not use this skill for tasks outside its scope.
