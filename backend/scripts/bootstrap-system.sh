#!/usr/bin/env sh
set -eu

exec python -m infrastructure.seed "$@"
