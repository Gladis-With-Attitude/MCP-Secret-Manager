#!/usr/bin/env sh
set -eu

usage() {
	cat <<'EOF'
Usage: scripts/postgres-backup.sh [--output FILE]

Create a PostgreSQL custom-format dump from the local Compose postgres service.

Environment:
  COMPOSE             Compose command to use. Defaults to "docker compose".
  ENV_FILE            Compose env file. Defaults to ".env.example".
  POSTGRES_SERVICE    Compose service name. Defaults to "postgres".
  BACKUP_DIR          Output directory. Defaults to "dist/backups/postgres".
  BACKUP_FILE         Output file path. Overrides BACKUP_DIR when set.
EOF
}

while [ "$#" -gt 0 ]; do
	case "$1" in
		--output)
			[ "$#" -ge 2 ] || {
				echo "--output requires a file path." >&2
				exit 2
			}
			BACKUP_FILE="$2"
			shift 2
			;;
		--help|-h)
			usage
			exit 0
			;;
		*)
			echo "Unknown option: $1" >&2
			usage >&2
			exit 2
			;;
	esac
done

COMPOSE="${COMPOSE:-docker compose}"
ENV_FILE="${ENV_FILE:-.env.example}"
POSTGRES_SERVICE="${POSTGRES_SERVICE:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-dist/backups/postgres}"

if [ -z "${BACKUP_FILE:-}" ]; then
	timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
	BACKUP_FILE="${BACKUP_DIR}/mcp-secret-manager-postgres-${timestamp}.dump"
fi

backup_parent="$(dirname "$BACKUP_FILE")"
mkdir -p "$backup_parent"
umask 077

tmp_file="${BACKUP_FILE}.tmp"
rm -f "$tmp_file"
trap 'rm -f "$tmp_file"' EXIT

$COMPOSE --env-file "$ENV_FILE" exec -T "$POSTGRES_SERVICE" sh -eu -c '
	if [ -n "${POSTGRES_PASSWORD:-}" ]; then
		export PGPASSWORD="$POSTGRES_PASSWORD"
	fi
	exec pg_dump \
		--format=custom \
		--no-owner \
		--no-privileges \
		--dbname="$POSTGRES_DB" \
		--username="$POSTGRES_USER"
' > "$tmp_file"

mv "$tmp_file" "$BACKUP_FILE"
trap - EXIT
chmod 600 "$BACKUP_FILE"
sha256sum "$BACKUP_FILE" > "${BACKUP_FILE}.sha256"
chmod 600 "${BACKUP_FILE}.sha256"

printf "PostgreSQL backup written to %s\n" "$BACKUP_FILE"
printf "Checksum written to %s\n" "${BACKUP_FILE}.sha256"
