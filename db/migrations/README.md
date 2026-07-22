# Database Migrations

PostgreSQL migrations live in this directory.

Migration files must be ordered, reviewed and tested. They must never contain
plaintext secret values, master keys, API tokens or private credentials.

The local Docker Compose stack applies migrations automatically through the
dedicated `migrations` service. Each migration command is serialized with a
PostgreSQL advisory lock configured in `env.py`.

Useful commands from the repository root:

```bash
make db-current
make db-history
make db-upgrade
make db-downgrade DB_DOWN_REVISION=-1
make db-revision DB_REVISION_MESSAGE="describe change"
make db-reset CONFIRM_RESET=dev
```
