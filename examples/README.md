# AI-SKILL — API Examples

Runnable code samples showing how to call the AI-SKILL REST API and
the Python / TypeScript SDKs.

## Files

| File                              | What it shows                                        |
|-----------------------------------|------------------------------------------------------|
| `rest/`                           | Direct HTTP calls (curl, httpie)                     |
| `python/`                         | Python SDK examples                                  |
| `typescript/`                     | TypeScript SDK examples                              |
| `postman/`                        | Postman / Bruno / Insomnia collection                |

## Quick start

```bash
# 1. Start the stack
make dev

# 2. Bootstrap an admin
make create-admin

# 3. Run an example
python examples/python/search.py "react hooks"
node  examples/typescript/search.ts "react hooks"
```

## Folder layout

```
examples/
├── README.md                  # this file
├── rest/
│   ├── auth.http              # register / login / refresh
│   ├── skills.http            # CRUD + search
│   └── README.md
├── python/
│   ├── auth.py                # register + login
│   ├── search.py              # semantic search
│   ├── create_skill.py        # POST a new skill
│   ├── paginated_list.py      # walk the full catalog
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

## Authentication, in 5 lines

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

## Semantic search

```python
results = client.search_skills(
    query="React performance optimization hooks",
    limit=10,
    category="frontend/react",
)
for r in results:
    print(f"{r.score:.3f}  {r.skill.name}")
```

See the per-language READMEs for the full API surface.
