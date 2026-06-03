# 配置参考

后端配置是 `backend/app/core/config.py` 中的一个 Pydantic v2 `Settings` 类。
在进程启动时从环境变量加载（带回退到 `.env` 文件）。

## 类

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    ...
```

按约定所有字段大写。`case_sensitive=True` 意味着环境变量名必须与字段名
完全一致。

## 分组

| 分组       | 字段                                              |
|------------|-------------------------------------------------|
| Application | `APP_NAME`、`APP_VERSION`、`DEBUG`、`API_PREFIX` |
| Database    | `DATABASE_URL`、`DATABASE_POOL_SIZE`、`DATABASE_MAX_OVERFLOW`、`DATABASE_POOL_TIMEOUT`、`DATABASE_POOL_RECYCLE` |
| Redis       | `REDIS_URL`、`REDIS_POOL_SIZE`                    |
| Qdrant      | `QDRANT_URL`、`QDRANT_API_KEY`                    |
| Auth        | `JWT_SECRET_KEY`、`JWT_ALGORITHM`、`ACCESS_TOKEN_EXPIRE_MINUTES`、`REFRESH_TOKEN_EXPIRE_DAYS` |
| CORS        | `BACKEND_CORS_ORIGINS`                            |
| Storage     | `STORAGE_TYPE`、`S3_BUCKET`、`S3_ACCESS_KEY`、`S3_SECRET_KEY`、`S3_REGION`、`S3_ENDPOINT_URL` |
| Embedding   | `EMBEDDING_MODEL`、`EMBEDDING_DIMENSION`          |
| Logging     | `LOG_LEVEL`、`LOG_FORMAT`                         |
| Rate limit  | `RATE_LIMIT_DEFAULT`、`RATE_LIMIT_WINDOW`         |
| Sentry      | `SENTRY_DSN`、`SENTRY_TRACES_SAMPLE_RATE`、`SENTRY_PROFILES_SAMPLE_RATE` |
| Admin       | `ADMIN_EMAIL`、`ADMIN_USERNAME`、`ADMIN_PASSWORD`、`ADMIN_FULL_NAME` |
| Locale      | `DEFAULT_LOCALE`、`SUPPORTED_LOCALES`             |

## 校验器

### `BACKEND_CORS_ORIGINS`

接受 Python 中的列表或环境变量中的逗号分隔字符串。

```bash
# 逗号分隔
BACKEND_CORS_ORIGINS=https://app.example.com,https://staging.example.com
```

### `enforce_jwt_secret_in_production`

`@model_validator(mode="after")` 实现：

- 生产环境：如果 `JWT_SECRET_KEY` 缺失、短于 32 字符或匹配已知弱默认值，则拒绝启动
- 调试环境：生成一个临时随机密钥并打日志告警

理由参见 [ADR 008](../adr/008-fail-fast-secrets.md)。

## 加载

设置加载一次并缓存：

```python
from app.core.config import get_settings, settings

# 在代码中任意位置：
db_url = settings.DATABASE_URL

# 或者，在 FastAPI 依赖中：
def my_route(settings: Settings = Depends(get_settings)):
    ...
```

缓存使用 `functools.lru_cache`，所以修改环境变量的测试在重读前
需要调用 `get_settings.cache_clear()`。

## 下一步

- [环境变量](environment.md) —— 每个变量、每个默认值、每个约束
- [配置（入门）](../getting-started/configuration.md)
- [源码](https://github.com/badhope/AI-SKILL/blob/main/backend/app/core/config.py)
