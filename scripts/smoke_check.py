"""Objective starter-repository checks. This script does not calculate marks."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "pyproject.toml",
    "README.md",
    "src/zimp/main.py",
    "src/zimp/domain/contracts.py",
    "src/zimp/support/fakes.py",
    "tests/test_contract.py",
    "docs/architecture-map.md",
)


def report(ok: bool, message: str) -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {message}")
    return ok


def main() -> int:
    results: list[bool] = []
    results.extend(report((ROOT / item).exists(), f"required path: {item}") for item in REQUIRED)

    src = ROOT / "src"
    sys.path.insert(0, str(src))
    for module in (
        "zimp.domain.contracts",
        "zimp.domain.game_state",
        "zimp.domain.basic_movement",
        "zimp.integration.game_controller",
        "zimp.support.fakes",
    ):
        results.append(report(importlib.util.find_spec(module) is not None, f"importable: {module}"))

    collection = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    results.append(report(collection.returncode == 0, "pytest collection succeeds"))
    if collection.returncode != 0:
        print(collection.stdout)
        print(collection.stderr)

    baseline = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    results.append(report(baseline.returncode == 0, "baseline pytest suite passes"))
    print(baseline.stdout.strip())
    if baseline.stderr.strip():
        print(baseline.stderr.strip())

    print("\nSmoke checks verify prerequisites only. They do not assess design quality,")
    print("integration reasoning, contribution, collaboration, or personal understanding.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
