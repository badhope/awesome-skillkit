# Postman / Insomnia / Bruno collection

A Postman-compatible collection that exercises the AI-SKILL REST API.
Same flows as `examples/rest/`, but in a format you can import and
run from a GUI client.

If you prefer a CLI / file-based client, head over to
[`examples/rest/`](../rest/) or
[`examples/python/`](../python/).

## Postman

```text
File  →  Import  →  File  →  examples/postman/ai-skill.postman_collection.json
```

The collection has two pre-defined variables:

| Variable  | Default value                  | Description           |
|-----------|--------------------------------|-----------------------|
| `baseUrl` | `http://localhost:8000/api/v1` | API base URL          |
| `token`   | (empty)                        | Bearer access token   |

The `Login` request writes its `access_token` to the `token`
variable automatically (via a `test` script). All other requests
use `Authorization: Bearer {{token}}`.

## Insomnia

Insomnia can import the same file:

```text
Application  →  Preferences  →  Data  →  Import Data  →  From File
```

…or use the menu:

```text
Insomnia  →  File  →  Import  →  examples/postman/ai-skill.postman_collection.json
```

## Bruno

Bruno is a file-based, git-friendly API client. Convert the
collection:

```bash
# Install the converter
npm install -g @usebruno/converters

# Convert
bru convert examples/postman/ai-skill.postman_collection.json
```

The output is a folder of `.bru` files you can check into your
fork.

## VS Code REST Client

If you prefer the REST Client extension, see the `examples/rest/`
folder — there are `.http` files that exercise the same flows.

## Where to go from here

- [Examples overview](../README.md)
- [REST (curl + .http)](../rest/README.md)
- [Python examples](../python/README.md)
- [TypeScript examples](../typescript/README.md)
