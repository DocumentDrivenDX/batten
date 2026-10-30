lint:
    uv run python scripts/quality.py --lint

test:
    uv run pytest

check:
    uv run python scripts/quality.py
