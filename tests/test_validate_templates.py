"""Tests for template validation (coverage reported to SonarCloud)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import TemplateError, TemplateNotFound
from jinja2.sandbox import SandboxedEnvironment

from scripts.validate_templates import (
    iter_template_files,
    main,
    run_validation,
    validate_jinja_yaml,
)

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
REPO_ROOT = Path(__file__).resolve().parent.parent


def test_repository_templates_are_valid() -> None:
    assert run_validation(TEMPLATES, quiet=True) == 0


def test_invalid_yaml_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "broken.yml").write_text("invalid: [\n", encoding="utf-8")
    assert run_validation(tmp_path, quiet=True) == 1


def test_invalid_jinja_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "bad.yml.j2").write_text("x: {{ unclosed\n", encoding="utf-8")
    assert run_validation(tmp_path, quiet=True) == 1


def test_whitespace_only_yaml_skipped(tmp_path: Path) -> None:
    (tmp_path / "empty.yml").write_text("   \n  \n", encoding="utf-8")
    assert run_validation(tmp_path, quiet=True) == 0


def test_whitespace_only_jinja_skipped(tmp_path: Path) -> None:
    (tmp_path / "empty.yml.j2").write_text("  \n", encoding="utf-8")
    assert run_validation(tmp_path, quiet=True) == 0


def test_jinja_renders_empty_no_yaml_phase(tmp_path: Path) -> None:
    (tmp_path / "only_comment.yml.j2").write_text("{# nothing #}\n", encoding="utf-8")
    assert run_validation(tmp_path, quiet=True) == 0


def test_missing_root_directory_is_ok() -> None:
    assert run_validation(REPO_ROOT / "nonexistent_dir_xyz", quiet=True) == 0


def test_non_yaml_extension_skipped(tmp_path: Path) -> None:
    (tmp_path / "readme.txt").write_text("hello", encoding="utf-8")
    assert run_validation(tmp_path, quiet=True) == 0


def test_iter_template_files_non_dir() -> None:
    assert iter_template_files(Path("/nonexistent_path_12345")) == []


def test_jinja_undefined_strict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    custom = Environment(
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        loader=FileSystemLoader(str(tmp_path)),
    )
    custom.globals["lookup"] = lambda *a, **k: ""
    p = tmp_path / "u.yml.j2"
    p.write_text("a: {{ undefined_name }}\n", encoding="utf-8")

    def _factory(_path: Path) -> Environment:
        return custom

    monkeypatch.setattr("scripts.validate_templates._jinja_env_for_template", _factory)
    with pytest.raises(ValueError, match="Jinja render error"):
        validate_jinja_yaml(p)


def test_jinja_template_load_error_non_syntax(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "t.yml.j2"
    p.write_text("x: 1\n", encoding="utf-8")

    def _boom(_self: SandboxedEnvironment, _name: str) -> None:
        raise TemplateNotFound("missing")

    monkeypatch.setattr(SandboxedEnvironment, "get_template", _boom)
    with pytest.raises(ValueError, match="Jinja template load error"):
        validate_jinja_yaml(p)


def test_jinja_template_error_on_render(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "t.yml.j2"
    p.write_text("x: 1\n", encoding="utf-8")
    mock_template = MagicMock()
    mock_template.render.side_effect = TemplateError("forced")

    def _fake_get(_self: SandboxedEnvironment, _name: str):
        return mock_template

    monkeypatch.setattr(SandboxedEnvironment, "get_template", _fake_get)
    with pytest.raises(ValueError, match="Jinja render error"):
        validate_jinja_yaml(p)


def test_oserror_while_reading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "a.yml"
    p.write_text("k: 1\n", encoding="utf-8")
    real = Path.read_text

    def patched_read(self: Path, *args, **kwargs):
        if self.resolve() == p.resolve():
            raise OSError("mock read failure")
        return real(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", patched_read)
    assert run_validation(tmp_path, quiet=True) == 1


def test_run_validation_prints_failure(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "b.yml").write_text("bad: [", encoding="utf-8")
    assert run_validation(tmp_path, quiet=False) == 1
    assert "Template validation failed" in capsys.readouterr().err


def test_run_validation_prints_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "ok.yml").write_text("k: 1\n", encoding="utf-8")
    assert run_validation(tmp_path, quiet=False) == 0
    assert "OK:" in capsys.readouterr().out


def test_main_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_templates", "--root", str(tmp_path)])
    assert main() == 0


def test_script_entrypoint() -> None:
    script = REPO_ROOT / "scripts" / "validate_templates.py"
    r = subprocess.run(
        [sys.executable, str(script), "--root", str(TEMPLATES)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert "OK:" in r.stdout
