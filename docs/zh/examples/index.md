可运行的代码示例，展示如何调用 AI-SKILL REST API 以及
Python / TypeScript SDK。

## 文件

| 文件                              | 内容                                           |
|-----------------------------------|------------------------------------------------|
| `rest/`                           | 直接 HTTP 调用（curl、httpie）                 |
| `python/`                         | Python SDK 示例                                |
| `typescript/`                     | TypeScript SDK 示例                            |
| `postman/`                        | Postman / Bruno / Insomnia 集合                |

## 快速上手

```bash
# 1. 启动整套服务
make dev

# 2. 引导管理员
make create-admin

# 3. 运行示例
python examples/python/search.py "react hooks"
node  examples/typescript/search.ts "react hooks"
```

## 目录结构

```
examples/
├── README.md                  # 本文件
├── rest/
│   ├── auth.http              # 注册 / 登录 / 刷新
│   ├── skills.http            # CRUD + 搜索
│   └── README.md
├── python/
│   ├── auth.py                # 注册 + 登录
│   ├── search.py              # 语义搜索
│   ├── create_skill.py        # POST 新技能
│   ├── paginated_list.py      # 遍历整个目录
│   └── README.md
├── typescript/
│   ├── auth.ts
│   ├── search.ts
│   ├── createSkill.ts
│   ├── paginatedList.ts
│   └── README.md
└── postman/
    └── ai-skill.postman_collection.json
```

## 5 行搞定认证

```python
# Python
from skill_sdk import SkillClient
client = SkillClient(base_url="http://localhost:8000")
client.login(email="you@example.com", password="hunter2")
me = client.get_current_user()
```

```typescript
// TypeScript
import { SkillClient } from '@ai-skill/sdk';
const client = new SkillClient({ baseUrl: 'http://localhost:8000' });
await client.login({ email: 'you@example.com', password: 'hunter2' });
const me = await client.getCurrentUser();
```

## 语义搜索

```python
results = client.search_skills(
    query="React performance optimization hooks",
    limit=10,
    category="frontend/react",
)
for r in results:
    print(f"{r.score:.3f}  {r.skill.name}")
```

完整 API 表面请参见各语言目录的 README。
