#!/usr/bin/env python3
"""
Health check script: verify all services are running and healthy.

Checks:
- PostgreSQL database connection
- Redis cache connection
- Qdrant vector database connection
- Backend API health endpoint
"""

import os
import sys
import time
from typing import Dict, Tuple

import httpx

DB_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/skill_db")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
API_URL = os.environ.get("API_URL", "http://localhost:8000")

CHECK_TIMEOUT = 10.0
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def check_postgres() -> Tuple[bool, str]:
    try:
        import asyncio

        import asyncpg

        dsn = DB_URL.replace("postgresql+asyncpg://", "postgresql://")

        async def _check():
            conn = await asyncpg.connect(dsn, timeout=CHECK_TIMEOUT)
            version = await conn.fetchval("SELECT version()")
            await conn.close()
            return str(version)

        result = asyncio.run(_check())
        return True, f"PostgreSQL OK: {result[:60]}..."
    except ImportError:
        return False, "asyncpg not installed"
    except Exception as e:
        return False, f"PostgreSQL ERROR: {e}"


def check_redis() -> Tuple[bool, str]:
    try:
        import redis
        client = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=CHECK_TIMEOUT)
        if client.ping():
            info = client.info("server")
            return True, f"Redis OK: {info.get('redis_version', 'unknown')}"
        return False, "Redis: Ping failed"
    except ImportError:
        return False, "redis-py not installed"
    except Exception as e:
        return False, f"Redis ERROR: {e}"


def check_qdrant() -> Tuple[bool, str]:
    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=CHECK_TIMEOUT) as client:
                resp = client.get(f"{QDRANT_URL}/health")
                if resp.status_code == 200:
                    return True, f"Qdrant OK (status: {resp.status_code})"
                resp = client.get(f"{QDRANT_URL}/collections")
                if resp.status_code == 200:
                    return True, f"Qdrant OK (status: {resp.status_code})"
                return False, f"Qdrant: Unexpected status {resp.status_code}"
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return False, f"Qdrant ERROR: {e}"
    return False, "Qdrant: Max retries exceeded"


def check_api() -> Tuple[bool, str]:
    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=CHECK_TIMEOUT) as client:
                resp = client.get(f"{API_URL}/health")
                if resp.status_code == 200:
                    data = resp.json()
                    return True, f"API OK: {data.get('app_name', 'unknown')} v{data.get('version', '?')}"
                return False, f"API: Status {resp.status_code}"
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return False, f"API ERROR: {e}"
    return False, "API: Max retries exceeded"


def print_status(service: str, success: bool, message: str) -> None:
    icon = "OK" if success else "FAIL"
    print(f"  [{icon}] {service}: {message}")


def main() -> int:
    print("=" * 60)
    print("  SERVICE HEALTH CHECK")
    print("=" * 60)
    print()

    checks: Dict[str, Tuple[bool, str]] = {}

    print("  Checking PostgreSQL...")
    checks["PostgreSQL"] = check_postgres()
    print_status("PostgreSQL", *checks["PostgreSQL"])

    print("  Checking Redis...")
    checks["Redis"] = check_redis()
    print_status("Redis", *checks["Redis"])

    print("  Checking Qdrant...")
    checks["Qdrant"] = check_qdrant()
    print_status("Qdrant", *checks["Qdrant"])

    print("  Checking API...")
    checks["API"] = check_api()
    print_status("API", *checks["API"])

    print()
    print("-" * 60)

    failed = [name for name, (ok, _) in checks.items() if not ok]
    passed = [name for name, (ok, _) in checks.items() if ok]

    print(f"  Results: {len(passed)}/{len(checks)} services healthy")

    if failed:
        print(f"  Failed services: {', '.join(failed)}")
        return 1

    print("  All services are healthy!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
