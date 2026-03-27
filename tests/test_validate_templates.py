"""Tests for template validation (coverage reported to SonarCloud)."""

from __future__ import annotations

from pathlib import Path

from scripts.validate_templates import run_validation

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "templates"


def test_repository_templates_are_valid() -> None:
    assert run_validation(TEMPLATES, quiet=True) == 0


def test_invalid_yaml_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "broken.yml").write_text("invalid: [\n", encoding="utf-8")
    assert run_validation(tmp_path, quiet=True) == 1


def test_invalid_jinja_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "bad.yml.j2").write_text("x: {{ unclosed\n", encoding="utf-8")
    assert run_validation(tmp_path, quiet=True) == 1
