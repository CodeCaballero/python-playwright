"""Given a diff file, print the files it touches, one per line.

Usage (from repo root, uses the project's venv):
    uv run python scripts/parse_diff.py <diff-file>
"""

import re
import sys
from pathlib import Path

DIFF_GIT_LINE = re.compile(r"^diff --git a/.+ b/(.+)$", re.MULTILINE)


def parse_diff(diff_text: str) -> list[str]:
    return DIFF_GIT_LINE.findall(diff_text)


def main(diff_path: str) -> None:
    diff_text = Path(diff_path).read_text()
    for file_path in parse_diff(diff_text):
        print(file_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    main(sys.argv[1])
