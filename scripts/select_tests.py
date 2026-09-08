"""Given a file listing changed app files (one per line), print which pytest
domain markers to run.

example
{
  "marker_expression": "login or transaction",
  "escalate": false,
  "unmatched_files": []
}

Usage (from repo root, uses the project's venv, needs config/ on the pythonpath):
    PYTHONPATH=. uv run python scripts/select_tests.py <touched-files-file>
"""

import fnmatch
import json
import sys
from pathlib import Path

import yaml
from config.paths import PROJECT_ROOT

MAP_PATH = PROJECT_ROOT / "test-impact-map.yml"


def select_markers(changed_files: list[str], impact_map: dict) -> dict:
    domains = impact_map["domains"]

    # Domains marked always_run (e.g. login) run no matter what changed.
    markers = {name for name, cfg in domains.items() if cfg.get("always_run")}
    unmatched_files = []

    for file_path in changed_files:
        domains_hit = [
            name
            for name, cfg in domains.items()
            if any(fnmatch.fnmatch(file_path, pattern) for pattern in cfg["app_globs"])
        ]
        if domains_hit:
            markers.update(domains_hit)
        else:
            # No domain claims this file: don't silently skip tests for it.
            unmatched_files.append(file_path)

    return {
        "marker_expression": " or ".join(sorted(markers)) if markers else None,
        "escalate": bool(unmatched_files),
        "unmatched_files": unmatched_files,
    }


def main(files_path: str) -> None:
    lines = Path(files_path).read_text().splitlines()
    changed_files = [line.strip() for line in lines if line.strip()]
    impact_map = yaml.safe_load(MAP_PATH.read_text())
    result = select_markers(changed_files, impact_map)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    main(sys.argv[1])
