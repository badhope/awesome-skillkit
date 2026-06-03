TypeScript / JavaScript SDK，提供了一个带类型的接口，用以与 AI-SKILL API 交互。

## 安装

```bash
npm install @skill-library/sdk
# 或
yarn add @skill-library/sdk
# 或
pnpm add @skill-library/sdk
```

## 快速上手

```typescript
import { SkillLibraryClient, SkillNotFoundError, AuthenticationError } from "@skill-library/sdk";

const client = new SkillLibraryClient({
  baseUrl: "https://api.skills.example.com",
  apiKey: "your-api-key",
  timeout: 30_000,
});

// 认证
const token = await client.auth.login({ username: "user", password: "pass" });
// 或
client.setToken("your-jwt-token");

// 列出技能
const result = await client.skills.list({
  categorySlug: "programming",
  search: "python",
  page: 1,
  pageSize: 20,
});
console.log(`共找到 ${result.total} 个技能`);
for (const skill of result.items) {
  console.log(`  - ${skill.name} (v${skill.version})`);
}

// 语义搜索
const search = await client.skills.search({ q: "machine learning", limit: 10 });
for (const r of search) {
  console.log(`  - ${r.name} (score: ${r.score.toFixed(2)})`);
}

// 获取单个技能
const skill = await client.skills.get("my-awesome-skill");
console.log(`${skill.name}: ${skill.description}`);

// 创建技能
const newSkill = await client.skills.create({
  name: "My New Skill",
  slug: "my-new-skill",
  description: "A powerful new skill",
  version: "1.0.0",
  categorySlug: "programming",
  tags: ["typescript", "ai"],
  content: { prompt: "You are a helpful assistant..." },
});

// 更新技能
await client.skills.update("my-new-skill", {
  description: "Updated description",
  version: "1.1.0",
});

// 精选 / 热门 / 趋势
const featured = await client.skills.getFeatured(5);
const popular = await client.skills.getPopular(5);
const trending = await client.skills.getTrending(5);

// 版本
const versions = await client.skills.getVersions("my-skill");
await client.skills.createVersion("my-skill", {
  version: "1.2.0",
  content: { prompt: "Updated prompt" },
  changelog: "Improved accuracy by 20%",
});

// 依赖
const deps = await client.skills.getDependencies("my-skill");
await client.skills.addDependency("my-skill", {
  dependsOnSkillSlug: "base-skill",
  versionConstraint: ">=1.0",
});
await client.skills.removeDependency("my-skill", { depId: "..." });

// 相似技能
const similar = await client.skills.getSimilar("my-skill", 5);

// 评分
await client.skills.rate("my-skill", { rating: 4, comment: "Great skill!" });

// 使用埋点
await client.skills.logUsage("my-skill", { action: "download" });

// 分类
const categories = await client.categories.list();
const tree = await client.categories.tree();

// 标签
const tags = await client.tags.popular(20);

// 分析
const dashboard = await client.analytics.dashboard();
const trends = await client.analytics.skillUsage(30);

// 组合
const compositions = await client.compositions.list();
const composition = await client.compositions.create({
  name: "My Workflow",
  slug: "my-workflow",
  description: "A composed workflow",
});

// 删除
await client.skills.delete("my-new-skill");
```

## 错误处理

```typescript
import {
  SkillLibraryClient,
  SkillNotFoundError,
  AuthenticationError,
  PermissionDeniedError,
  RateLimitError,
  ValidationError,
  APIError,
  ConnectionError,
} from "@skill-library/sdk";

const client = new SkillLibraryClient({ baseUrl: "https://api.skills.example.com" });

try {
  const skill = await client.skills.get("non-existent-skill");
} catch (err) {
  if (err instanceof SkillNotFoundError) {
    console.log(`未找到技能: ${err.message}`);
  } else if (err instanceof AuthenticationError) {
    console.log(`认证失败: ${err.message}`);
  } else if (err instanceof RateLimitError) {
    console.log(`被限流，${err.retryAfter} 秒后重试`);
  } else if (err instanceof ValidationError) {
    console.log(`数据非法: ${err.message}`);
  } else if (err instanceof PermissionDeniedError) {
    console.log(`禁止访问: ${err.message}`);
  } else if (err instanceof ConnectionError) {
    console.log(`连接失败: ${err.message}`);
  } else if (err instanceof APIError) {
    console.log(`API 错误 (${err.statusCode}): ${err.message}`);
  } else {
    throw err;
  }
}
```

## 配置项

客户端接受以下 `ClientConfig` 选项：

| 选项           | 类型                  | 默认值                  | 描述                          |
|----------------|-----------------------|-------------------------|-------------------------------|
| `baseUrl`      | `string`              | `http://localhost:8000` | AI-SKILL API 基地址            |
| `apiKey`       | `string`              | —                       | 认证用的 API 密钥              |
| `token`        | `string`              | —                       | JWT access token（`apiKey` 的替代） |
| `timeout`      | `number`（毫秒）       | `30000`                 | 单次请求超时                   |
| `maxRetries`   | `number`              | `3`                     | 临时性失败的最大重试次数        |
| `retryDelay`   | `number`（毫秒）       | `1000`                  | 初始退避时长（指数）            |
| `headers`      | `Record<string,string>`| `{}`                    | 每次请求都会附带的额外头部      |

## 构建

```bash
npm install
npm run build
```

通过 `tsup` 产物为 `dist/index.js`（CJS）、`dist/index.mjs`（ESM）
与 `dist/index.d.ts`（类型定义）。

## 许可证

MIT
