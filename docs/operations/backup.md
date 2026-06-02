# Backup & restore

A production deployment is only as good as its backup story. This
page covers the three stateful services and the minimal restore
drill.

## What to back up

| Service    | Data to back up                        | Frequency |
|------------|----------------------------------------|-----------|
| PostgreSQL | The whole database                     | Daily     |
| Qdrant     | The `skills` collection snapshot       | Weekly    |
| Redis      | Cache only — losing it is non-fatal    | None      |
| Object storage (if S3) | Bucket contents                | Continuous (versioning) |

## PostgreSQL

### Snapshot

```bash
docker compose exec -T postgres pg_dump \
    -U skill_user \
    -d skill_db \
    --no-owner \
    --no-privileges \
    | gzip > "backup-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
```

### Restore

```bash
# 1. Stop the backend so nothing writes while we restore
docker compose stop backend worker beat

# 2. Drop and recreate the database
gunzip -c backup-20260601T000000Z.sql.gz | \
    docker compose exec -T postgres psql -U skill_user -d skill_db

# 3. Start everything back up
docker compose up -d
```

### Cron job (sample)

```cron
# /etc/cron.d/skill-system-backup
0 3 * * * cd /opt/skill-system && \
  /usr/local/bin/backup-postgres.sh >> /var/log/skill-backup.log 2>&1
```

`backup-postgres.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /opt/skill-system
KEEP=14
BACKUP_FILE="/var/backups/skill/postgres-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
docker compose exec -T postgres pg_dump -U skill_user skill_db \
  | gzip > "$BACKUP_FILE"
# Prune old backups
find /var/backups/skill -name 'postgres-*.sql.gz' -mtime +$KEEP -delete
```

## Qdrant

Qdrant has a built-in snapshot API.

### Create a snapshot

```bash
curl -X POST 'http://localhost:6333/collections/skills/snapshots'
```

The snapshot is written to the container's `/qdrant/snapshots/`
directory.

### Copy it out

```bash
docker cp skill-qdrant:/qdrant/snapshots ./qdrant-snapshots
```

### Restore

```bash
# 1. Stop the backend
docker compose stop backend worker beat

# 2. Stop Qdrant
docker compose stop qdrant

# 3. Copy the snapshot back
docker cp ./qdrant-snapshots/<snapshot-name> skill-qdrant:/qdrant/snapshots/

# 4. Start Qdrant and trigger the restore
docker compose start qdrant
curl -X PUT 'http://localhost:6333/collections/skills/snapshots/recover' \
  -H 'Content-Type: application/json' \
  -d "{\"location\": \"/qdrant/snapshots/<snapshot-name>\"}"

# 5. Start the rest
docker compose up -d
```

## Redis

Losing Redis is non-fatal — the application will rebuild the cache
on the next request. The only thing in Redis is:

- Session denylist (for logged-out JWTs)
- Rate-limit counters
- Generic cache entries

No backup is needed.

## Object storage

If you use S3 or a compatible service:

- Enable **bucket versioning** so a delete is recoverable
- Set a **lifecycle policy** to move old versions to Glacier /
  cold storage after 30 days
- Replicate the bucket to a second region

## Restore drill

A backup you have never restored is a backup you cannot trust.
**Quarterly** run a restore drill:

1. Spin up a fresh VM (or use a staging environment).
2. Restore the latest Postgres snapshot.
3. Restore the latest Qdrant snapshot.
4. Start the stack with restored data.
5. Run `make health-check`.
6. Spot-check a few search queries.
7. Tear down the drill environment.

Document the time and the result.

## Where to go from here

- [Deployment](../deployment.md) — production topologies
- [Troubleshooting](../troubleshooting.md) — what to do if a restore
  goes wrong
