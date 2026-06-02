# AI-SKILL — Python SDK examples

## Install

```bash
pip install skill-sdk
# or, from source:
cd sdk/python && pip install -e .
```

## Configure

The SDK reads the following environment variables:

| Variable       | Default                          | Purpose           |
|----------------|----------------------------------|-------------------|
| `SKILL_BASE_URL` | `http://localhost:8000`         | API base URL      |
| `SKILL_API_KEY`  | (unset)                         | Optional API key   |

Or pass them directly to the constructor.

## Files

| File                       | Purpose                            |
|----------------------------|------------------------------------|
| `auth.py`                  | Register, login, refresh, logout   |
| `search.py`                | Semantic vector search             |
| `create_skill.py`          | POST a new skill                   |
| `paginated_list.py`        | Walk the full catalog page by page |

## Usage

```python
from skill_sdk import SkillClient

client = SkillClient(base_url="http://localhost:8000")
client.login(email="you@example.com", password="SuperSecret123!")

for skill in client.list_skills(category="frontend", page_size=20):
    print(skill.name)
```

See the per-file examples for the long form.
