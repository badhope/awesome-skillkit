本目录包含一个兼容 Postman 的集合，用于演练 AI-SKILL REST API。

## Postman

```text
File  →  Import  →  File  →  examples/postman/ai-skill.postman_collection.json
```

该集合预定义了两个变量：

| 变量       | 默认值                            | 说明              |
|------------|-----------------------------------|-------------------|
| `baseUrl`  | `http://localhost:8000/api/v1`    | API 基地址         |
| `token`    | （空）                            | Bearer access token |

`Login` 请求会通过 `test` 脚本将其 `access_token` 自动写入 `token`
变量。其他所有请求都使用 `Authorization: Bearer {{token}}`。

## Insomnia

Insomnia 也能导入同一文件：

```text
Application  →  Preferences  →  Data  →  Import Data  →  From File
```

或使用菜单：

```text
Insomnia  →  File  →  Import  →  examples/postman/ai-skill.postman_collection.json
```

## Bruno

Bruno 是一个基于文件、对 Git 友好的 API 客户端。可用以下方式
转换该集合：

```bash
# 安装转换器
npm install -g @usebruno/converters

# 转换
bru convert examples/postman/ai-skill.postman_collection.json
```

输出会是一个包含若干 `.bru` 文件的目录，可以提交到你的 fork。

## VS Code REST Client

如果你更喜欢 REST Client 扩展，请参见 `examples/rest/` 目录
—— 那里有覆盖同样流程的 `.http` 文件。

## 接下来去哪里

- [示例总览](../)
- [REST（curl + .http）](rest.md)
- [Python 示例](python.md)
- [TypeScript 示例](typescript.md)
