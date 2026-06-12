---
name: hotkey
name_zh: hotkey
description: Add or edit LobeHub keyboard shortcuts. Use for HotkeyEnum, 
  HOTKEYS_REGISTRATION,
description_zh: Add or edit LobeHub keyboard shortcuts. Use for HotkeyEnum, 
  HOTKEYS_REGISTRATION,
category: dev-tools
tags:
  - ai
  - cli
  - frontend
  - llm
  - python
source:
language: en
needs_review: false
slug: hotkey
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

Use this skill when you need to work with hotkey.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# Adding Keyboard Shortcuts Guide

## Steps to Add a New Hotkey

### 1. Update Hotkey Constant

In `src/types/hotkey.ts`:

```typescript
export const HotkeyEnum = {
  // existing...
  ClearChat: 'clearChat', // Add new
} as const;
```

### 2. Register Default Hotkey

In `src/const/hotkeys.ts`:

```typescript
import { KeyMapEnum as Key, combineKeys } from '@lobehub/ui';

export const HOTKEYS_REGISTRATION: HotkeyRegistration = [
  {
    group: HotkeyGroupEnum.Conversation,
    id: HotkeyEnum.ClearChat,
    keys: combineKeys([Key.Mod, Key.Shift, Key.Backspace]),
    scopes: [HotkeyScopeEnum.Chat],
  },
];
```

### 3. Add i18n Translation

In `src/locales/default/hotkey.ts`:

```typescript
const hotkey: HotkeyI18nTranslations = {
  clearChat: {
    desc: '清空当前会话的所有消息记录',
    title: '清空聊天记录',
  },
};
```

### 4. Create and Register Hook

In `src/hooks/useHotkeys/chatScope.ts`:

```typescript
export const useClearChatHotkey = () => {
  const clearMessages = useChatStore((s) => s.clearMessages);
  return useHotkeyById(HotkeyEnum.ClearChat, clearMessages);
};

export const useRegisterChatHotkeys = () => {
  useClearChatHotkey();
  // ...other hotkeys
};
```

### 5. Add Tooltip (Optional)

```tsx
const clearChatHotkey = useUserStore(settingsSelectors.getHotkeyById(HotkeyEnum.ClearChat));

<Tooltip hotkey={clearChatHotkey} title={t('clearChat.title', { ns: 'hotkey' })}>
  <Button icon={<DeleteOutlined />} onClick={clearMessages} />
</Tooltip>;
```

## Best Practices

1. **Scope**: Choose global or chat scope based on functionality
2. **Grouping**: Place in appropriate group (System/Layout/Conversation)
3. **Conflict check**: Ensure no conflict with system/browser shortcuts
4. **Platform**: Use `Key.Mod` instead of hardcoded `Ctrl` or `Cmd`
5. **Clear description**: Provide title and description for users

## Troubleshooting

- **Not working**: Check scope and RegisterHotkeys hook
- **Not in settings**: Verify HOTKEYS_REGISTRATION config
- **Conflict**: HotkeyInput component shows warnings
- **Page-specific**: Ensure correct scope activation

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 hotkey 技能
skill = load_skill("hotkey")
result = skill.execute()
print(result)
```

