#!/usr/bin/env sh
set -eu

usage() {
	cat <<'EOF'
Usage: RESTORE_CONFIRM=replace scripts/postgres-restore.sh BACKUP_FILE

Restore a PostgreSQL custom-format dump into the local Compose postgres service.

Environment:
  COMPOSE             Compose command to use. Defaults to "docker compose".
  ENV_FILE            Compose env file. Defaults to ".env.example".
  POSTGRES_SERVICE    Compose service name. Defaults to "postgres".
  RESTORE_CONFIRM     Must be exactly "replace".
EOF
}

case "${1:-}" in
	--help|-h)
		usage
		exit 0
		;;
esac

if [ "$#" -ne 1 ]; then
	usage >&2
	exit 2
fi

BACKUP_FILE="$1"
COMPOSE="${COMPOSE:-docker compose}"
ENV_FILE="${ENV_FILE:-.env.example}"
POSTGRES_SERVICE="${POSTGRES_SERVICE:-postgres}"

if [ ! -f "$BACKUP_FILE" ]; then
	echo "Backup file does not exist: $BACKUP_FILE" >&2
	exit 1
fi

if [ "${RESTORE_CONFIRM:-}" != "replace" ]; then
	echo "Refusing to restore without RESTORE_CONFIRM=replace." >&2
	exit 1
fi

$COMPOSE --env-file "$ENV_FILE" exec -T "$POSTGRES_SERVICE" sh -eu -c '
	if [ -n "${POSTGRES_PASSWORD:-}" ]; then
		export PGPASSWORD="$POSTGRES_PASSWORD"
	fi
	exec pg_restore \
		--clean \
		--if-exists \
		--single-transaction \
		--exit-on-error \
		--no-owner \
		--no-privileges \
		--dbname="$POSTGRES_DB" \
		--username="$POSTGRES_USER"
' < "$BACKUP_FILE"

printf "PostgreSQL restore completed from %s\n" "$BACKUP_FILE"
