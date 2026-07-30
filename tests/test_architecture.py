import ast
from pathlib import Path


def imported_modules(path: Path) -> set[str]:
    modules: set[str] = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_domain_package_does_not_import_tkinter() -> None:
    domain = Path("src/zimp/domain")
    imports = {
        module
        for path in domain.glob("*.py")
        for module in imported_modules(path)
    }
    assert not any(module == "tkinter" or module.startswith("tkinter.") for module in imports)


def test_ui_module_imports_without_creating_a_window() -> None:
    import pytest

    pytest.importorskip("_tkinter", reason="Tk runtime unavailable in this environment")
    import zimp.ui.tk_app  # noqa: F401
