lint:
    uv run python scripts/check.py --lint

test:
    uv run pytest
    bun run test:native

check:
    uv run python scripts/check.py

# Build original pinned platform SDKs and install the isolated application cohort.
approval-prepare:
    uv run python scripts/prepare_approval.py

# Explicit deployment into a new fabricated local database, never implicit startup.
approval-init:
    .cache/approval-runtime/bin/python -I -m approval_desk.cli init

approval:
    .cache/approval-runtime/bin/python -I -m approval_desk.cli serve

approval-test:
    bun run test:native

# Rebuild only the app against the already prepared platform cohort.
approval-refresh:
    uv run python scripts/prepare_approval.py --app-only
