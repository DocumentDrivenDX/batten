"""Mechanical native grant setup for the registered browser scenario."""

import sys
from pathlib import Path

import psycopg
from pgserver.postgres_server import get_server


def main() -> None:
    server = get_server(Path(sys.argv[1]) / "pgdata", cleanup_mode=None)
    try:
        with psycopg.connect(server.get_uri(), autocommit=True) as admin:
            admin.execute("REVOKE approval_reviewers FROM approval_blake")
    finally:
        server.cleanup()


if __name__ == "__main__":
    main()
