# SDKs

AI-SKILL ships two first-party client libraries with the same
public surface. The Python SDK is async-first; the TypeScript SDK
works in both Node and the browser.

## Pick your language

| Language   | Use it from                | Install                                     |
|------------|----------------------------|---------------------------------------------|
| Python     | Backend, scripts, ML       | `pip install skill-sdk`                     |
| TypeScript | Frontend, Node, Edge       | `npm install @skill-library/sdk`            |

Both SDKs:

- Cover the same endpoints with the same method names
- Type their request and response payloads
- Handle token storage and refresh transparently
- Surface errors as a typed hierarchy

## Public surface

The full per-language reference is in each SDK's README.

- [Python SDK reference](python.md)
- [TypeScript SDK reference](typescript.md)

A short overview of the common methods:

| Method                     | What it does                              |
|----------------------------|-------------------------------------------|
| `register(...)`            | Create a new user                         |
| `login(email, password)`   | Exchange credentials for a token pair     |
| `refresh(refreshToken)`    | Rotate an expiring access token           |
| `logout()`                 | Invalidate the current token              |
| `getCurrentUser()`         | Fetch the authenticated user              |
| `listCategories()`         | List categories                           |
| `listSkills({...})`        | List skills with filters and pagination   |
| `iterSkills({...})`        | Async iterator over the full catalog      |
| `getSkill(slug)`           | Fetch a single skill                      |
| `createSkill({...})`       | Create a skill                            |
| `updateSkill(slug, ...)`   | Update a skill                            |
| `deleteSkill(slug)`        | Delete a skill                            |
| `searchSkills({...})`      | Semantic + lexical search                 |
| `listCompositions()`       | List compositions                         |
| `createComposition({...})` | Create a composition                      |

The Python SDK methods are *snake_case*; the TypeScript SDK methods
are *camelCase*. Field names follow the same convention.

## Authentication

Both SDKs use the same pattern:

=== "Python"

    ```python
    from skill_sdk import SkillClient

    with SkillClient(base_url="http://localhost:8000") as client:
        client.login(email="you@example.com", password="hunter2")
        me = client.get_current_user()
    ```

=== "TypeScript"

    ```typescript
    import { SkillLibraryClient } from "@skill-library/sdk";

    const client = new SkillLibraryClient({ baseUrl: "http://localhost:8000" });
    await client.auth.login({ email: "you@example.com", password: "hunter2" });
    const me = await client.auth.me();
    ```

By default, the SDK stores the token in memory; it is lost when the
process exits. Pass a custom `tokenStore` (Python) or `tokenStorage`
(TS) to persist it:

=== "Python"

    ```python
    # persist to a file
    client = SkillClient(
        base_url="...",
        token_store=FileTokenStore("~/.skill-sdk-token"),
    )
    ```

=== "TypeScript"

    ```typescript
    // browser
    const client = new SkillLibraryClient({
      baseUrl: "...",
      tokenStorage: new LocalStorageTokenStorage(),
    });

    // Node
    const client = new SkillLibraryClient({
      baseUrl: "...",
      tokenStorage: new FileTokenStorage("/path/to/token.json"),
    });
    ```

## Errors

Both SDKs surface a hierarchy:

| Error                   | When                                           |
|-------------------------|------------------------------------------------|
| `ConnectionError`       | Connection refused, DNS failure, TLS error     |
| `RateLimitError`        | 429 — slow down                                |
| `AuthenticationError`   | 401 — bad credentials, expired token           |
| `PermissionDeniedError` | 403 — authenticated but not allowed            |
| `SkillNotFoundError`    | 404 — resource missing                         |
| `ValidationError`       | 422 — request payload is invalid               |
| `APIError`              | Any other 4xx / 5xx response                   |

Each error carries:

- `statusCode` — the HTTP status
- `message` — a human-readable string
- `errorCode` — the machine-readable code from the response body
- `requestId` — useful when reporting bugs

## Versioning

The SDKs follow [Semantic Versioning](https://semver.org/):

- **Major** — breaking change to the public surface
- **Minor** — new method, new field
- **Patch** — bugfix, doc, internal refactor

A major version of the SDK targets a major version of the backend.
The SDK is tested against the current and previous major backend
version.

## Where to go from here

- [Python SDK](python.md)
- [TypeScript SDK](typescript.md)
- [REST examples](../examples/rest.md) — for everything the
  SDK does not (yet) expose
