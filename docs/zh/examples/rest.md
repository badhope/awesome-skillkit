你可以直接通过 HTTP 调用 API。`*.http` 文件兼容
[VS Code REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)；
`*.sh` 文件是普通 bash 脚本。

## 前置准备

```bash
export API="http://localhost:8000/api/v1"
```

## 1. 注册

```bash
curl -s -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "username": "you",
    "password": "SuperSecret123!",
    "full_name": "Your Name"
  }' | jq
```

响应（200）：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { "id": "...", "email": "you@example.com", "username": "you" }
}
```

## 2. 登录

```bash
curl -s -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "SuperSecret123!"
  }' | jq -r .access_token > /tmp/jwt

export TOKEN=$(cat /tmp/jwt)
```

## 3. 获取当前用户

```bash
curl -s "$API/users/me" -H "Authorization: Bearer $TOKEN" | jq
```

## 4. 列出技能（分页）

```bash
curl -s "$API/skills?page=1&size=20" | jq
```

## 5. 语义搜索

```bash
curl -s -X POST "$API/skills/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "React performance optimization hooks",
    "limit": 10,
    "min_score": 0.6
  }' | jq
```

## 6. 创建技能

```bash
curl -s -X POST "$API/skills" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "React useMemo deep-dive",
    "slug": "react-usememo-deep-dive",
    "description": "A practical guide to React useMemo with examples",
    "content": "# React useMemo\n\n...",
    "category_id": "<uuid-of-the-frontend-category>",
    "tags": ["react", "performance"],
    "version": "1.0.0",
    "is_public": true
  }' | jq
```

## 7. 刷新 access token

```bash
curl -s -X POST "$API/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<REFRESH_TOKEN>"}' | jq
```

## 8. 登出

```bash
curl -s -X POST "$API/auth/logout" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## HTTP 文件语法（VS Code REST Client）

```http
### 注册
POST http://localhost:8000/api/v1/auth/register
Content-Type: application/json

{
  "email": "you@example.com",
  "username": "you",
  "password": "SuperSecret123!",
  "full_name": "Your Name"
}

### 登录
# @name login
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "you@example.com",
  "password": "SuperSecret123!"
}

###
@token = {{login.response.body.access_token}}

### 获取 me
GET http://localhost:8000/api/v1/users/me
Authorization: Bearer {{token}}
```

完整文件请参见本目录的 `auth.http` 与 `skills.http`。
