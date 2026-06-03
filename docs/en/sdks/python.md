Python SDK provides a clean, typed interface to interact with the Modern Skill Library API.

## Installation

```bash
pip install skill-sdk
# or with poetry
poetry add skill-sdk
```

## Quick Start

```python
from skill_sdk import SkillClient

# Initialize client
client = SkillClient(
    base_url="https://api.skills.example.com",
    api_key="your-api-key",
    timeout=30.0,
)

# Authentication
token = client.auth.login(username="user", password="pass")
# Or set token directly
client.set_token("your-jwt-token")

# List skills
result = client.skills.list(
    category_slug="programming",
    search="python",
    page=1,
    page_size=20,
)
print(f"Found {result.total} skills")
for skill in result.items:
    print(f"  - {skill.name} (v{skill.version})")

# Search with vector similarity
results = client.skills.search(q="machine learning", limit=10)
for r in results:
    print(f"  - {r.name} (score: {r.score:.2f})")

# Get a single skill
skill = client.skills.get("my-awesome-skill")
print(f"{skill.name}: {skill.description}")

# Create a skill
new_skill = client.skills.create({
    "name": "My New Skill",
    "slug": "my-new-skill",
    "description": "A powerful new skill",
    "version": "1.0.0",
    "category_slug": "programming",
    "tags": ["python", "ai"],
    "content": {"prompt": "You are a helpful assistant..."},
})

# Update a skill
client.skills.update("my-new-skill", {
    "description": "Updated description",
    "version": "1.1.0",
})

# Get featured/popular/trending
featured = client.skills.get_featured(limit=5)
popular = client.skills.get_popular(limit=5)
trending = client.skills.get_trending(limit=5)

# Version management
versions = client.skills.get_versions("my-skill")
client.skills.create_version("my-skill", {
    "version": "1.2.0",
    "content": {"prompt": "Updated prompt"},
    "changelog": "Improved accuracy by 20%",
})

# Dependency management
deps = client.skills.get_dependencies("my-skill")
client.skills.add_dependency("my-skill", {
    "depends_on_skill_slug": "base-skill",
    "version_constraint": ">=1.0",
})
client.skills.remove_dependency("my-skill", dep_id="...")

# Find similar skills
similar = client.skills.get_similar("my-skill", limit=5)

# Rate a skill
client.skills.rate("my-skill", rating=4, comment="Great skill!")

# Usage tracking
client.skills.log_usage("my-skill", action="download")

# Categories
categories = client.categories.list()
tree = client.categories.tree()

# Tags
tags = client.tags.popular(limit=20)

# Analytics
dashboard = client.analytics.dashboard()
trends = client.analytics.skill_usage(days=30)

# Compositions
compositions = client.compositions.list()
composition = client.compositions.create({
    "name": "My Workflow",
    "slug": "my-workflow",
    "description": "A composed workflow",
})

# Delete
client.skills.delete("my-new-skill")

# Close connection
client.close()

# Or use as context manager
with SkillClient(base_url="https://api.skills.example.com") as client:
    skills = client.skills.list(page_size=5)
```

## Error Handling

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
    print(f"Skill not found: {e}")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except ValidationError as e:
    print(f"Invalid data: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except APIError as e:
    print(f"API error ({e.status_code}): {e}")
```

## Configuration

- `base_url`: Base URL of the Skill Library API (default: http://localhost:8000)
- `api_key`: API key for authentication
- `timeout`: Request timeout in seconds (default: 30.0)
- `max_retries`: Maximum retry attempts for failed requests (default: 3)
- `retry_delay`: Initial delay between retries in seconds (default: 1.0, uses exponential backoff)