"""Register, log in, and read the current user with the Python SDK."""
from __future__ import annotations

import os

from skill_sdk import SkillClient, SkillError


def main() -> int:
    base_url = os.environ.get("SKILL_BASE_URL", "http://localhost:8000")
    email = os.environ.get("SKILL_EMAIL", "you@example.com")
    password = os.environ.get("SKILL_PASSWORD", "SuperSecret123!")

    with SkillClient(base_url=base_url) as client:
        # 1. Register (idempotent — swallows the 409 on a re-run)
        try:
            client.register(
                email=email,
                username=email.split("@")[0],
                password=password,
                full_name="Example User",
            )
            print(f"✓ Registered {email}")
        except SkillError as e:
            if e.status_code == 409:
                print(f"… {email} already exists, logging in")
            else:
                raise

        # 2. Log in
        tokens = client.login(email=email, password=password)
        print(f"✓ Logged in. access_token expires in "
              f"{tokens.expires_in}s")

        # 3. Read the current user
        me = client.get_current_user()
        print(f"✓ Hello, {me.full_name} ({me.email})")

        # 4. Refresh the access token
        new_tokens = client.refresh(refresh_token=tokens.refresh_token)
        print(f"✓ Refreshed access token, expires in "
              f"{new_tokens.expires_in}s")

        # 5. Logout
        client.logout()
        print("✓ Logged out")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
