You can hit the API with plain HTTP. The `*.http` files are
[VS Code REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
compatible; the `*.sh` files are plain bash.

## Prerequisites

```bash
export API="http://localhost:8000/api/v1"
```

## 1. Register

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

Response (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { "id": "...", "email": "you@example.com", "username": "you" }
}
```

## 2. Login

```bash
curl -s -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "SuperSecret123!"
  }' | jq -r .access_token > /tmp/jwt

export TOKEN=$(cat /tmp/jwt)
```

## 3. Get the current user

```bash
curl -s "$API/users/me" -H "Authorization: Bearer $TOKEN" | jq
```

## 4. List skills (paginated)

```bash
curl -s "$API/skills?page=1&size=20" | jq
```

## 5. Semantic search

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

## 6. Create a skill

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

## 7. Refresh the access token

```bash
curl -s -X POST "$API/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<REFRESH_TOKEN>"}' | jq
```

## 8. Logout

```bash
curl -s -X POST "$API/auth/logout" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## HTTP file syntax (VS Code REST Client)

```http
### Register
POST http://localhost:8000/api/v1/auth/register
Content-Type: application/json

{
  "email": "you@example.com",
  "username": "you",
  "password": "SuperSecret123!",
  "full_name": "Your Name"
}

### Login
# @name login
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "you@example.com",
  "password": "SuperSecret123!"
}

###
@token = {{login.response.body.access_token}}

### Get me
GET http://localhost:8000/api/v1/users/me
Authorization: Bearer {{token}}
```

See `auth.http` and `skills.http` in this folder for the full files.
