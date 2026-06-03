# SDK

AI-SKILL 提供两套一等公民的客户端库，两者的公共接口完全一致。Python SDK
以异步为优先；TypeScript SDK 同时支持 Node 与浏览器。

## 选择语言

| 语言       | 适用场景                 | 安装命令                                    |
|------------|--------------------------|---------------------------------------------|
| Python     | 后端、脚本、机器学习     | `pip install skill-sdk`                     |
| TypeScript | 前端、Node、Edge         | `npm install @skill-library/sdk`            |

两套 SDK 都具备：

- 覆盖相同端点，方法名一致
- 对请求与响应载荷进行类型化
- 自动处理令牌的存储与刷新
- 以类型化层级方式暴露错误

## 公共接口

完整、按语言分类的参考位于各 SDK 自身的 README。

- [Python SDK 参考](../sdks/python/)
- [TypeScript SDK 参考](../sdks/typescript/)

常用方法概览：

| 方法                          | 作用                                        |
|-------------------------------|---------------------------------------------|
| `register(...)`               | 创建新用户                                  |
| `login(email, password)`      | 用凭证换取令牌对                            |
| `refresh(refreshToken)`       | 轮换即将过期的 access token                 |
| `logout()`                    | 撤销当前令牌                                |
| `getCurrentUser()`            | 获取当前已登录用户                          |
| `listCategories()`            | 列出分类                                    |
| `listSkills({...})`           | 列出技能，支持过滤与分页                    |
| `iterSkills({...})`           | 异步迭代全量技能目录                        |
| `getSkill(slug)`              | 获取单个技能                                |
| `createSkill({...})`          | 创建一个技能                                |
| `updateSkill(slug, ...)`      | 更新一个技能                                |
| `deleteSkill(slug)`           | 删除一个技能                                |
| `searchSkills({...})`         | 语义 + 词法搜索                             |
| `listCompositions()`          | 列出组合                                    |
| `createComposition({...})`    | 创建一个组合                                |

Python SDK 的方法名为 *snake_case*；TypeScript SDK 的方法名为 *camelCase*。
字段名遵循同一约定。

## 认证

两套 SDK 的模式相同：

=== "Python"

    ```python
    from skill_sdk import SkillClient

    with SkillClient(base_url="http://localhost:8000") as client:
        client.login(email="you@example.com", password="hunter2")
        me = client.get_current_user()
    ```

=== "TypeScript"

    ```typescript
    import { SkillLibraryClient } from "@skill-library/sdk";

    const client = new SkillLibraryClient({ baseUrl: "http://localhost:8000" });
    await client.auth.login({ email: "you@example.com", password: "hunter2" });
    const me = await client.auth.me();
    ```

默认情况下，SDK 将令牌保存在内存中；进程退出即丢失。传入自定义
`tokenStore`（Python）或 `tokenStorage`（TS）即可持久化：

=== "Python"

    ```python
    # 持久化到文件
    client = SkillClient(
        base_url="...",
        token_store=FileTokenStore("~/.skill-sdk-token"),
    )
    ```

=== "TypeScript"

    ```typescript
    // 浏览器
    const client = new SkillLibraryClient({
      baseUrl: "...",
      tokenStorage: new LocalStorageTokenStorage(),
    });

    // Node
    const client = new SkillLibraryClient({
      baseUrl: "...",
      tokenStorage: new FileTokenStorage("/path/to/token.json"),
    });
    ```

## 错误

两套 SDK 都暴露一个错误层级：

| 错误                       | 触发场景                                       |
|----------------------------|------------------------------------------------|
| `ConnectionError`          | 连接被拒、DNS 失败、TLS 错误                  |
| `RateLimitError`           | 429 —— 限流，请放慢                           |
| `AuthenticationError`      | 401 —— 凭证错误或令牌过期                      |
| `PermissionDeniedError`    | 403 —— 已认证但无权限                          |
| `SkillNotFoundError`       | 404 —— 资源不存在                              |
| `ValidationError`          | 422 —— 请求载荷不合法                          |
| `APIError`                 | 其他 4xx / 5xx 响应                            |

每个错误都包含：

- `statusCode` —— HTTP 状态码
- `message` —— 人类可读描述
- `errorCode` —— 响应体中的机器可读错误码
- `requestId` —— 报告 bug 时很有用

## 版本策略

两套 SDK 均遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- **Major** —— 公共接口破坏性变更
- **Minor** —— 新方法、新字段
- **Patch** —— 缺陷修复、文档、内部重构

SDK 的 major 版本对应后端的 major 版本。SDK 会针对当前与上一 major
版本的后端进行测试。

## 接下来去哪里

- [Python SDK](../sdks/python/)
- [TypeScript SDK](../sdks/typescript/)
- [REST 示例](../examples/rest/) —— 涵盖 SDK 暂未（还）暴露的部分
