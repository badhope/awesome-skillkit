## 安装

```bash
npm install @ai-skill/sdk
# 或从源码安装：
cd sdk/typescript && npm install && npm run build && npm link
cd ../../frontend && npm link @ai-skill/sdk
```

## 配置

SDK 读取以下环境变量：

| 变量                | 默认值                       | 用途              |
|---------------------|------------------------------|-------------------|
| `SKILL_BASE_URL`    | `http://localhost:8000`      | API 基地址         |
| `SKILL_API_KEY`     | （未设置）                   | 可选的 API 密钥    |

也可以直接传给构造函数。

## 文件

| 文件                  | 用途                                  |
|-----------------------|---------------------------------------|
| `auth.ts`             | 注册、登录、刷新、登出                |
| `search.ts`           | 语义搜索                              |
| `createSkill.ts`      | POST 新建技能                         |
| `paginatedList.ts`    | 遍历整个目录                          |

## 用法

```typescript
import { SkillClient } from '@ai-skill/sdk';

const client = new SkillClient({ baseUrl: 'http://localhost:8000' });
await client.login({ email: 'you@example.com', password: 'hunter2' });
for await (const skill of client.iterSkills({ pageSize: 20, isPublic: true })) {
  console.log(skill.name);
}
```

详细示例见各文件。
