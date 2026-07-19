from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs"
PLAN_LINK = re.compile(r"(?i)(?:^|[(/])plans/")


def _nav_targets(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(target for item in value for target in _nav_targets(item))
    if isinstance(value, dict):
        return tuple(target for item in value.values() for target in _nav_targets(item))
    raise AssertionError(f"Unsupported navigation value: {value!r}")


def test_navigation_exactly_covers_documentation_pages() -> None:
    config = tomllib.loads((ROOT / "zensical.toml").read_text(encoding="utf-8"))
    targets = _nav_targets(config["project"]["nav"])
    pages = {path.relative_to(DOCS).as_posix() for path in DOCS.rglob("*.md")}
    assert len(targets) == len(set(targets)), "navigation contains duplicate pages"
    assert set(targets) == pages


def test_maintained_docs_do_not_depend_on_plan_files() -> None:
    assert not (ROOT / "plans").exists()
    for path in (ROOT / "README.md", *DOCS.rglob("*.md")):
        assert not PLAN_LINK.search(path.read_text(encoding="utf-8")), path


def test_release_history_matches_current_version_and_baseline() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    release_history = (DOCS / "releases.md").read_text(encoding="utf-8")

    assert f"## {project['project']['version']}" in release_history
    assert "Before: 0.5.0" in release_history
    assert "After: 1.0.0" in release_history
    assert "`6efb9ff`" in release_history
