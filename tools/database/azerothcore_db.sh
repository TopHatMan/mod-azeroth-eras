#!/usr/bin/env bash

set -euo pipefail

PROGRAM_NAME="$(basename "$0")"

usage() {
    cat <<EOF
Usage:
  ${PROGRAM_NAME} backup --database NAME --output-dir DIR [connection options]
  ${PROGRAM_NAME} restore --database NAME --snapshot FILE.sql.gz \\
      --confirm-database NAME --pre-restore-dir DIR [connection options]

Connection options:
  --defaults-extra-file FILE  MySQL client option file (recommended)
  --host HOST                 Database host
  --port PORT                 Database port
  --user USER                 Database user

This tool never accepts a password on the command line. Put credentials in a
permission-restricted MySQL option file or use your normal client configuration.
EOF
}

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

validate_database_name() {
    [[ "$1" =~ ^[A-Za-z0-9_-]+$ ]] ||
        die "database names may contain only letters, numbers, underscores, and hyphens"
}

database=""
output_dir=""
snapshot=""
confirmation=""
pre_restore_dir=""
defaults_extra_file=""
db_host=""
db_port=""
db_user=""

[[ $# -gt 0 ]] || { usage >&2; exit 2; }
command_name="$1"
shift
if [[ "$command_name" == "--help" || "$command_name" == "-h" ]]; then
    usage
    exit 0
fi
[[ "$command_name" == "backup" || "$command_name" == "restore" ]] || {
    usage >&2
    die "command must be backup or restore"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --database) database="${2:-}"; shift 2 ;;
        --output-dir) output_dir="${2:-}"; shift 2 ;;
        --snapshot) snapshot="${2:-}"; shift 2 ;;
        --confirm-database) confirmation="${2:-}"; shift 2 ;;
        --pre-restore-dir) pre_restore_dir="${2:-}"; shift 2 ;;
        --defaults-extra-file) defaults_extra_file="${2:-}"; shift 2 ;;
        --host) db_host="${2:-}"; shift 2 ;;
        --port) db_port="${2:-}"; shift 2 ;;
        --user) db_user="${2:-}"; shift 2 ;;
        --help|-h) usage; exit 0 ;;
        *) die "unknown argument: $1" ;;
    esac
done

[[ -n "$database" ]] || die "--database is required"
validate_database_name "$database"

if [[ -n "$defaults_extra_file" && ! -f "$defaults_extra_file" ]]; then
    die "MySQL option file does not exist: $defaults_extra_file"
fi

connection_args=()
[[ -n "$defaults_extra_file" ]] && connection_args+=("--defaults-extra-file=$defaults_extra_file")
[[ -n "$db_host" ]] && connection_args+=("--host=$db_host")
[[ -n "$db_port" ]] && connection_args+=("--port=$db_port")
[[ -n "$db_user" ]] && connection_args+=("--user=$db_user")

create_backup() {
    local target_database="$1"
    local target_dir="$2"
    local timestamp base temporary sql_file checksum_file metadata_file

    require_command mysqldump
    require_command gzip
    require_command sha256sum
    [[ -n "$target_dir" ]] || die "backup output directory is required"
    mkdir -p "$target_dir"
    [[ -d "$target_dir" && -w "$target_dir" ]] || die "backup directory is not writable: $target_dir"

    timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
    base="${target_database}-${timestamp}"
    sql_file="$target_dir/${base}.sql.gz"
    checksum_file="${sql_file}.sha256"
    metadata_file="${sql_file}.metadata"
    [[ ! -e "$sql_file" ]] || die "backup already exists: $sql_file"
    temporary="${sql_file}.partial.$$"

    if ! mysqldump "${connection_args[@]}" \
        --single-transaction --routines --triggers --events --hex-blob --add-drop-database \
        --databases "$target_database" | gzip -9 > "$temporary"; then
        rm -f "$temporary"
        die "database dump failed for $target_database"
    fi
    mv "$temporary" "$sql_file"
    (
        cd "$target_dir"
        sha256sum "$(basename "$sql_file")" > "$(basename "$checksum_file")"
    )
    {
        printf 'format=azerothcore-db-snapshot-v1\n'
        printf 'database=%s\n' "$target_database"
        printf 'created_utc=%s\n' "$timestamp"
        printf 'snapshot=%s\n' "$(basename "$sql_file")"
        printf 'checksum=%s\n' "$(basename "$checksum_file")"
    } > "$metadata_file"

    printf '%s\n' "$sql_file"
}

case "$command_name" in
    backup)
        [[ -n "$output_dir" ]] || die "--output-dir is required for backup"
        create_backup "$database" "$output_dir"
        ;;
    restore)
        require_command mysql
        require_command gzip
        require_command sha256sum
        [[ -n "$snapshot" ]] || die "--snapshot is required for restore"
        [[ -f "$snapshot" ]] || die "snapshot does not exist: $snapshot"
        [[ -f "${snapshot}.sha256" ]] || die "checksum sidecar does not exist: ${snapshot}.sha256"
        [[ -f "${snapshot}.metadata" ]] || die "metadata sidecar does not exist: ${snapshot}.metadata"
        [[ "$confirmation" == "$database" ]] ||
            die "--confirm-database must exactly match the target database"
        [[ -n "$pre_restore_dir" ]] ||
            die "--pre-restore-dir is required; restore always takes a rescue snapshot first"

        snapshot_database="$(sed -n 's/^database=//p' "${snapshot}.metadata")"
        [[ "$snapshot_database" == "$database" ]] ||
            die "snapshot metadata is for database '$snapshot_database', not '$database'"
        read -r expected_checksum _ < "${snapshot}.sha256"
        [[ "$expected_checksum" =~ ^[0-9a-fA-F]{64}$ ]] || die "snapshot checksum sidecar is malformed"
        actual_checksum="$(sha256sum "$snapshot")"
        actual_checksum="${actual_checksum%% *}"
        [[ "$actual_checksum" == "$expected_checksum" ]] || die "snapshot checksum validation failed"

        printf 'Creating pre-restore rescue snapshot of %s...\n' "$database" >&2
        rescue_snapshot="$(create_backup "$database" "$pre_restore_dir")"
        printf 'Rescue snapshot: %s\n' "$rescue_snapshot" >&2
        printf 'Restoring verified snapshot into %s...\n' "$database" >&2
        gzip --decompress --stdout "$snapshot" | mysql "${connection_args[@]}" "$database"
        printf 'Restore completed for %s.\n' "$database" >&2
        ;;
esac
