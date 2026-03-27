#!/usr/bin/env python3
"""
Validate Envgene templates under templates/:
  - *.yml / *.yaml: strict YAML parse (no Jinja processing).
  - *.j2 / *.yml.j2: Jinja via FileSystemLoader + get_template (no from_string), then YAML parse.

Exit code 1 if any file fails.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from jinja2 import ChainableUndefined, FileSystemLoader
from jinja2.exceptions import TemplateError, TemplateSyntaxError, UndefinedError
from jinja2.sandbox import SandboxedEnvironment
from yaml import YAMLError


def _is_jinja_template(path: Path) -> bool:
    return path.suffix == ".j2" or path.name.endswith(".yml.j2") or path.name.endswith(".yaml.j2")


def _ansible_lookup_stub(*_args, **_kwargs) -> str:
    """Stand-in for Ansible's lookup() used in a few namespace templates."""
    return ""


def _jinja_env_for_template(path: Path) -> SandboxedEnvironment:
    """Sandboxed env with loader rooted at the template file directory (load by file name, not from_string)."""
    loader = FileSystemLoader(str(path.resolve().parent))
    env = SandboxedEnvironment(
        loader=loader,
        undefined=ChainableUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["lookup"] = _ansible_lookup_stub
    return env


def _load_yaml_documents(text: str, path: Path) -> None:
    try:
        list(yaml.safe_load_all(text))
    except YAMLError as e:
        raise ValueError(f"YAML parse error in {path}: {e}") from e


def validate_plain_yaml(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return
    _load_yaml_documents(text, path)


def validate_jinja_yaml(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return
    env = _jinja_env_for_template(path)
    try:
        template = env.get_template(path.name)
    except TemplateSyntaxError as e:
        raise ValueError(f"Jinja syntax error: {e}") from e
    except TemplateError as e:
        raise ValueError(f"Jinja template load error: {e}") from e
    try:
        rendered = template.render()
    except UndefinedError as e:
        raise ValueError(f"Jinja render error (missing variable or filter): {e}") from e
    except TemplateError as e:
        raise ValueError(f"Jinja render error: {e}") from e
    if not rendered.strip():
        return
    _load_yaml_documents(rendered, path)


def iter_template_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    out: list[Path] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".yml", ".yaml", ".j2"}:
            continue
        out.append(p)
    return out


def run_validation(root: Path, *, quiet: bool = False) -> int:
    """
    Validate all template files under root. Returns 0 on success, 1 if any file fails.
    """
    errors: list[tuple[Path, str]] = []
    files = iter_template_files(root)

    for path in files:
        try:
            if _is_jinja_template(path):
                validate_jinja_yaml(path)
            else:
                validate_plain_yaml(path)
        except ValueError as e:
            errors.append((path, str(e)))
        except OSError as e:
            errors.append((path, str(e)))

    if errors:
        if not quiet:
            print("Template validation failed:\n", file=sys.stderr)
            for path, msg in errors:
                print(f"  {path}: {msg}", file=sys.stderr)
        return 1

    if not quiet:
        print(f"OK: {len(files)} file(s) under {root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate templates/ YAML and Jinja templates.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "templates",
        help="Directory to scan (default: repo templates/)",
    )
    args = parser.parse_args()
    return run_validation(args.root, quiet=False)


if __name__ == "__main__":
    sys.exit(main())
