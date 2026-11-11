"""Keep large generated files (evidence, binaries, receipts) out of git."""

from __future__ import annotations

import subprocess
from pathlib import Path

MAX_FILE_BYTES = 1_000_000
MAX_TREE_BYTES = 3_000_000


def problems(sizes: dict[str, int]) -> list[str]:
    found = [
        f"{path}: {size} bytes exceeds the {MAX_FILE_BYTES} byte file limit"
        for path, size in sorted(sizes.items())
        if size > MAX_FILE_BYTES
    ]
    total = sum(sizes.values())
    if total > MAX_TREE_BYTES:
        found.append(f"tracked tree is {total} bytes; limit is {MAX_TREE_BYTES}")
    return found


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    names = subprocess.run(
        ["git", "ls-files"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    sizes = {
        name: (root / name).stat().st_size for name in names if (root / name).is_file()
    }
    found = problems(sizes)
    if found:
        raise SystemExit("\n".join(found))
    print(f"{len(sizes)} tracked files, {sum(sizes.values())} bytes: within limits.")


if __name__ == "__main__":
    main()
