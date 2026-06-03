## 安装

```bash
pip install skill-sdk
# 或从源码安装：
cd sdk/python && pip install -e .
```

## 配置

SDK 读取以下环境变量：

| 变量                | 默认值                       | 用途              |
|---------------------|------------------------------|-------------------|
| `SKILL_BASE_URL`    | `http://localhost:8000`      | API 基地址         |
| `SKILL_API_KEY`     | （未设置）                   | 可选的 API 密钥    |

也可以直接传给构造函数。

## 文件

| 文件                       | 用途                                  |
|----------------------------|---------------------------------------|
| `auth.py`                  | 注册、登录、刷新、登出                |
| `search.py`                | 语义向量搜索                          |
| `create_skill.py`          | POST 新建技能                         |
| `paginated_list.py`        | 逐页遍历整个目录                      |

## 用法

```python
from skill_sdk import SkillClient

client = SkillClient(base_url="http://localhost:8000")
client.login(email="you@example.com", password="SuperSecret123!")

for skill in client.list_skills(category="frontend", page_size=20):
    print(skill.name)
```

详细示例见各文件。
