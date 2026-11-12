#!/bin/bash
set -eu
unset PYTHONPATH PYTHONHOME PYTHONOPTIMIZE
export PYTHONNOUSERSITE=1
export FIXTURE_DATA_DIR="$PWD/logs"
mkdir -p "$FIXTURE_DATA_DIR"
platform=$1
if [ "$platform" = macos ]; then
    python=$2
    pg=$3
    uv_bin=$4
    export UV_CACHE_DIR="$PWD/uv-cache"
    for cohort in reader admin; do
        "$uv_bin" venv --offline --no-python-downloads --python "$python" "$cohort-env"
        "$uv_bin" pip install --offline --no-index --require-hashes --only-binary :all: \
            --python "$cohort-env/bin/python" --find-links "${cohort}_wheels" -r "$cohort.lock"
        "$uv_bin" pip check --python "$cohort-env/bin/python"
    done
    mkdir -p pg-socket
    "$pg/initdb" -D "$PWD/pg-data" -U postgres --no-locale --encoding=UTF8 \
        --auth-local=trust --auth-host=reject >logs/initdb.log
    "$pg/pg_ctl" -D "$PWD/pg-data" -l "$PWD/logs/postgres.log" \
        -o "-c listen_addresses='' -c unix_socket_directories=$PWD/pg-socket" -w start
    trap '"$pg/pg_ctl" -D "$PWD/pg-data" -m fast -w stop' EXIT
    export FIXTURE_DATABASE_URI="host=$PWD/pg-socket dbname=postgres user=postgres"
else
    for cohort in reader admin; do
        python -m venv --without-pip "$cohort-env"
        python -m pip --python "$cohort-env/bin/python" install --no-index --require-hashes --only-binary :all: \
            --find-links reader_wheels -r "$cohort.lock"
        python -m pip --python "$cohort-env/bin/python" check
    done
fi
reader=reader-env/bin/python
admin=admin-env/bin/python
"$reader" verify_installed.py 32 >logs/reader-installed.json
"$admin" verify_installed.py 8 >logs/admin-installed.json
export FIXTURE_HTTP_PORT=$("$reader" -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])')
"$admin" apply_migration21.py >logs/initial-result.json
"$reader" macos_probe.py >logs/host-result.json 2>logs/host-stderr.log
"$admin" apply_forward.py >logs/forward-result.json
