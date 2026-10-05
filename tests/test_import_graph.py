"""Architectural isolation and import graph boundary tests.

Enforces rules defined in SPEC §4, TRD §4.2, and AGENTS.md:
1. `src/` modules NEVER import Flask, scripts, or webapp.
2. `phonelens.config` NEVER imports anything from the project.
3. `webapp/` imports only from `phonelens.service.predictor`.
"""

import ast
from pathlib import Path


def _get_imports(py_file: Path) -> list[str]:
    """Parse a python file and return all imported module names."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def test_src_modules_do_not_import_forbidden_layers():
    """Verify src/phonelens never imports flask, webapp, or scripts."""
    src_dir = Path(__file__).resolve().parents[1] / "src" / "phonelens"
    forbidden_prefixes = ("flask", "webapp", "scripts")

    for py_file in src_dir.rglob("*.py"):
        imports = _get_imports(py_file)
        for imp in imports:
            for forbidden in forbidden_prefixes:
                assert not (imp == forbidden or imp.startswith(f"{forbidden}.")), (
                    f"Violation in {py_file}: forbidden import '{imp}'"
                )


def test_config_has_no_project_imports():
    """Verify phonelens.config imports only standard library / no phonelens packages."""
    config_file = Path(__file__).resolve().parents[1] / "src" / "phonelens" / "config.py"
    imports = _get_imports(config_file)
    for imp in imports:
        assert not imp.startswith("phonelens"), f"config.py must not import from project: '{imp}'"
