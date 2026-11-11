"""The size guard flags oversized files and an oversized tree."""

from __future__ import annotations

from check_tree_size import MAX_FILE_BYTES, MAX_TREE_BYTES, problems


def test_small_tree_passes() -> None:
    assert problems({"a.py": 10, "uv.lock": 100_000}) == []


def test_large_file_and_large_tree_are_reported() -> None:
    (message,) = problems({"evidence/run.json": MAX_FILE_BYTES + 1})
    assert "evidence/run.json" in message
    many = {
        f"f{i}": MAX_FILE_BYTES for i in range(MAX_TREE_BYTES // MAX_FILE_BYTES + 1)
    }
    assert any("tracked tree" in text for text in problems(many))
