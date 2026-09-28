# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The layering rules of docs/technical/Source-Code.md, checked on every module's imports.

  domain  imports only itself and the standard library
  app     imports the domain and itself, never infra: it is handed infra
  infra   may import the domain, never the app
  and only the composition root, src/markdown-kit.py, imports infra and app together
"""
import ast
import sys
import unittest

from tests import support

LAYERS = ("domain", "app", "infra")
ALLOWED = {"domain": {"domain"}, "app": {"domain", "app"}, "infra": {"domain", "infra"}}


def imports(path) -> list[tuple[int, str]]:
    """Every module a file imports, by its top-level name, with the line; a relative import is its own layer."""
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    layer = path.relative_to(support.SRC).parts[0]
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [(node.lineno, a.name.split(".")[0]) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            found.append((node.lineno, layer if node.level else (node.module or "").split(".")[0]))
    return found


class LayeringTest(unittest.TestCase):
    def modules(self, layer):
        files = sorted((support.SRC / layer).rglob("*.py"))
        self.assertTrue(files, layer)
        return files

    def test_each_layer_imports_only_what_it_may(self):
        stdlib = set(sys.stdlib_module_names) | {"__future__"}
        for layer in LAYERS:
            for path in self.modules(layer):
                for line, name in imports(path):
                    if name in stdlib:
                        continue
                    self.assertIn(name, ALLOWED[layer], f"{path.relative_to(support.ROOT)}:{line} imports {name}")

    def test_the_domain_does_no_io(self):
        banned = {"open", "subprocess", "urllib", "socket", "os", "shutil", "tempfile", "pathlib", "zoneinfo"}
        for path in self.modules("domain"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    names = {(node.module or "").split(".")[0]}
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
                    names = {"open"}
                else:
                    continue
                self.assertFalse(names & banned, f"{path.relative_to(support.ROOT)}:{node.lineno} uses {names & banned}")

    def test_only_the_composition_root_imports_infra_and_app(self):
        for path in sorted(support.SRC.glob("*.py")):
            self.assertEqual(path.name, "markdown-kit.py", f"{path.name} is a second entry point")
        names = set()
        tree = ast.parse(support.LAUNCHER.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        self.assertTrue({"app", "infra"} <= names)


if __name__ == "__main__":
    unittest.main()
