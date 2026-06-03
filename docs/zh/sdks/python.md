Python SDK 提供了一个干净、带类型的接口，用以与 Modern Skill Library API 交互。

## 安装

```bash
pip install skill-sdk
# 或使用 poetry
poetry add skill-sdk
```

## 快速上手

```python
from skill_sdk import SkillClient

# 初始化客户端
client = SkillClient(
    base_url="https://api.skills.example.com",
    api_key="your-api-key",
    timeout=30.0,
)

# 认证
token = client.auth.login(username="user", password="pass")
# 或直接设置令牌
client.set_token("your-jwt-token")

# 列出技能
result = client.skills.list(
    category_slug="programming",
    search="python",
    page=1,
    page_size=20,
)
print(f"共找到 {result.total} 个技能")
for skill in result.items:
    print(f"  - {skill.name} (v{skill.version})")

# 向量相似度搜索
results = client.skills.search(q="machine learning", limit=10)
for r in results:
    print(f"  - {r.name} (score: {r.score:.2f})")

# 获取单个技能
skill = client.skills.get("my-awesome-skill")
print(f"{skill.name}: {skill.description}")

# 创建技能
new_skill = client.skills.create({
    "name": "My New Skill",
    "slug": "my-new-skill",
    "description": "A powerful new skill",
    "version": "1.0.0",
    "category_slug": "programming",
    "tags": ["python", "ai"],
    "content": {"prompt": "You are a helpful assistant..."},
})

# 更新技能
client.skills.update("my-new-skill", {
    "description": "Updated description",
    "version": "1.1.0",
})

# 获取精选 / 热门 / 趋势技能
featured = client.skills.get_featured(limit=5)
popular = client.skills.get_popular(limit=5)
trending = client.skills.get_trending(limit=5)

# 版本管理
versions = client.skills.get_versions("my-skill")
client.skills.create_version("my-skill", {
    "version": "1.2.0",
    "content": {"prompt": "Updated prompt"},
    "changelog": "Improved accuracy by 20%",
})

# 依赖管理
deps = client.skills.get_dependencies("my-skill")
client.skills.add_dependency("my-skill", {
    "depends_on_skill_slug": "base-skill",
    "version_constraint": ">=1.0",
})
client.skills.remove_dependency("my-skill", dep_id="...")

# 查找相似技能
similar = client.skills.get_similar("my-skill", limit=5)

# 评分
client.skills.rate("my-skill", rating=4, comment="Great skill!")

# 使用埋点
client.skills.log_usage("my-skill", action="download")

# 分类
categories = client.categories.list()
tree = client.categories.tree()

# 标签
tags = client.tags.popular(limit=20)

# 分析
dashboard = client.analytics.dashboard()
trends = client.analytics.skill_usage(days=30)

# 组合
compositions = client.compositions.list()
composition = client.compositions.create({
    "name": "My Workflow",
    "slug": "my-workflow",
    "description": "A composed workflow",
})

# 删除
client.skills.delete("my-new-skill")

# 关闭连接
client.close()

# 或作为上下文管理器使用
with SkillClient(base_url="https://api.skills.example.com") as client:
    skills = client.skills.list(page_size=5)
```

## 错误处理

```python
from skill_sdk import (
    SkillClient,
    SkillNotFoundError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
    ConnectionError,
)

client = SkillClient(base_url="https://api.skills.example.com")

try:
    skill = client.skills.get("non-existent-skill")
except SkillNotFoundError as e:
    print(f"未找到技能: {e}")
except AuthenticationError as e:
    print(f"认证失败: {e}")
except RateLimitError as e:
    print(f"被限流，{e.retry_after} 秒后重试")
except ValidationError as e:
    print(f"数据非法: {e}")
except ConnectionError as e:
    print(f"连接失败: {e}")
except APIError as e:
    print(f"API 错误 ({e.status_code}): {e}")
```

## 配置项

- `base_url`：Skill Library API 的基地址（默认：`http://localhost:8000`）
- `api_key`：用于认证的 API 密钥
- `timeout`：请求超时时间（秒，默认 `30.0`）
- `max_retries`：失败请求的最大重试次数（默认 `3`）
- `retry_delay`：重试初始间隔（秒，默认 `1.0`，采用指数退避）
