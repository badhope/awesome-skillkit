## Supported Versions

Security updates are provided for the latest stable release and, when applicable, one previous minor version.

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

We take the security of AI-SKILL seriously. If you discover a security vulnerability, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

### Reporting Process

1. **Email** the details to the maintainers at the security contact listed on the repository
2. Include a detailed description of the vulnerability:
   - Affected component(s) and version(s)
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
3. Allow time for the vulnerability to be addressed before any public disclosure

### Response Timeline

| Phase | Expected Timeframe |
|-------|-------------------|
| Initial acknowledgment | Within 48 hours |
| Confirmation and assessment | Within 5 business days |
| Fix development and testing | Within 14 business days |
| Coordinated disclosure | After fix is released |

Critical vulnerabilities will be prioritized accordingly.

### What to Expect

- You will receive an acknowledgment of your report within 48 hours
- We will keep you informed of our progress throughout the process
- We will credit you in the release notes (unless you prefer to remain anonymous)
- A CVE identifier will be requested if applicable

---

## Security Best Practices

### For Deployers

1. **Always change default secrets** — Never use the example JWT secret in production. Generate a strong key:
   ```bash
   openssl rand -hex 32
   ```
   The application **refuses to start in production** (`DEBUG=false`) if `JWT_SECRET_KEY`
   is missing, shorter than 32 characters, or matches a known-weak default. In
   `DEBUG=true` mode an ephemeral random key is generated per-process and a warning
   is logged, which keeps development frictionless but is **not** safe for
   production.

2. **Bootstrap the first admin securely** — Set `ADMIN_PASSWORD` (≥ 12 chars) in
   your `.env` before the first start so `app.core.seed` can create the initial
   superuser, or run the dedicated CLI:
   ```bash
   ADMIN_PASSWORD="$(openssl rand -base64 18)" \\
   ADMIN_EMAIL="ops@yourdomain.com" \\
   ADMIN_USERNAME="ops" \\
   python -m app.scripts.create_admin
   ```
   If neither path is taken, the application logs a CRITICAL line on startup
   and **skips** admin seeding — every fresh database therefore requires an
   explicit operator action to enable admin login.

3. **Use TLS** — Always run behind a reverse proxy (Nginx, Traefik, Caddy) with TLS termination enabled

4. **Restrict CORS origins** — Set `BACKEND_CORS_ORIGINS` to only your actual frontend domains. Wildcard origins are not supported because the API sets `allow_credentials=true`.

5. **Enable rate limiting** — Configure `RATE_LIMIT_DEFAULT` and `RATE_LIMIT_WINDOW` appropriately

6. **Regular updates** — Keep dependencies updated with `poetry update` and `npm update`

7. **Database security** — Use strong passwords, restrict network access, enable SSL connections. The `POSTGRES_PASSWORD` value in `docker-compose.yml` is sourced from `.env` and is intentionally left empty if not set so the container fails fast rather than starting with a known weak default.

8. **Environment isolation** — Use separate `.env` files for development, staging, and production

### For Contributors

1. **Never commit secrets** — API keys, passwords, and tokens must never be committed
2. **Use `.env.example`** as a template only; actual values go in `.env` (gitignored)
3. **Validate inputs** — All user input must be validated server-side
4. **Sanitize outputs** — Prevent XSS by sanitizing user-generated content
5. **Principle of least privilege** — Database users should have minimal required permissions
6. **Review dependencies** — Check for known vulnerabilities before adding new dependencies

---

## Vulnerability Disclosure Policy

AI-SKILL follows a coordinated disclosure model:

1. Reporter submits vulnerability privately
2. Maintainers verify and assess the vulnerability
3. A fix is developed and tested
4. A security release is published
5. Public disclosure occurs after users have had reasonable time to update

We request that you do not publicly disclose the vulnerability until we have had sufficient time to address it. We aim to resolve critical issues within 14 days and will coordinate disclosure timing with you.

---

## Security Features

AI-SKILL implements several security measures:

- **Authentication**: JWT with access/refresh token rotation
- **Authorization**: Role-Based Access Control (RBAC)
- **Input Validation**: Pydantic schema validation on all API inputs
- **Rate Limiting**: Configurable per-endpoint and global rate limits
- **CORS**: Configurable cross-origin resource sharing policies
- **Password Hashing**: bcrypt with appropriate work factor
- **Password Policy**: minimum 8 chars with upper, lower, and digit; weak-password denylist
- **Security Headers**: `SecurityHeadersMiddleware` adds HSTS (production only),
  `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
  `Permissions-Policy`, strict `Content-Security-Policy`, and the
  `Cross-Origin-*` isolation headers. The `Server` and `X-Powered-By` headers
  are also sanitized to avoid fingerprinting.
- **Startup Secret Validation**: production refuses to start without a
  32+ char `JWT_SECRET_KEY` that is not on a weak-default denylist. The
  same policy applies to `ADMIN_PASSWORD` in production seeding.
- **HTTPS**: Recommended TLS termination at reverse proxy level
- **Audit Logging**: All authentication and modification events are logged
- **Dependency Scanning**: Automated vulnerability scanning in CI pipeline

---

## Acknowledgments

We appreciate the security research community's efforts in responsibly disclosing vulnerabilities. Security researchers who report valid vulnerabilities will be acknowledged in our release notes and this document (with permission).