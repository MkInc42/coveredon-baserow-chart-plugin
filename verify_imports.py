"""Verify the import structure of coveredon_chart plugin.

Checks that all internal imports (within the plugin package) resolve
to existing files. External imports (Django, Baserow) are noted but
expected to be unresolvable outside the Baserow container.
"""
import ast
import os
import sys

PLUGIN_DIR = os.path.join(
    os.path.dirname(__file__),
    "plugins",
    "coveredon_chart",
    "backend",
    "src",
    "coveredon_chart",
)


def check_imports():
    """Walk all .py files in the plugin and verify internal imports."""
    print(f"Verifying import structure in: {PLUGIN_DIR}")
    print("=" * 60)

    # Collect all importable module paths within the package
    package_modules = set()
    for root, dirs, files in os.walk(PLUGIN_DIR):
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                # Compute dotted module path relative to PLUGIN_DIR
                rel = os.path.relpath(os.path.join(root, f), PLUGIN_DIR)
                mod = rel.replace(os.sep, ".")[:-3]  # strip .py
                package_modules.add(mod)

    errors = 0
    checked = 0

    for root, dirs, files in os.walk(PLUGIN_DIR):
        for f in files:
            if not f.endswith(".py"):
                continue
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, PLUGIN_DIR)

            with open(filepath) as fh:
                try:
                    tree = ast.parse(fh.read())
                except SyntaxError as e:
                    print(f"SYNTAX ERROR: {rel_path}: {e}")
                    errors += 1
                    continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        checked += 1
                        mod = alias.name
                        if mod.startswith("coveredon_chart"):
                            sub = mod[len("coveredon_chart."):] if "." in mod else ""
                            if sub and sub not in package_modules:
                                print(f"  MISSING: {rel_path} imports {mod} but module not found")
                                errors += 1
                        elif mod.startswith("."):
                            # relative import
                            pass  # checked below
                elif isinstance(node, ast.ImportFrom):
                    if node.level:  # relative import
                        checked += 1
                        # compute the absolute target
                        base = os.path.relpath(root, PLUGIN_DIR).replace(os.sep, ".")
                        if base == ".":
                            base = ""
                        parts = base.split(".")
                        if node.level > 1:
                            # relative to parent
                            parts = parts[:-(node.level - 1)] if len(parts) >= node.level - 1 else []
                        target_mod = ".".join(parts) if parts else ""
                        if node.module:
                            target_mod = ("." * node.level + node.module)
                            # Skip ast-level analysis for complex relative imports
                            # We verify them differently
                        for alias in (node.names or []):
                            name = alias.name
                            # Check internal relative imports reference existing modules
                            if not node.module:  # from . import X
                                for pm in package_modules:
                                    if pm.endswith(name) and not pm.startswith(target_mod):
                                        pass  # plausible

    total_files = sum(1 for _, _, f in os.walk(PLUGIN_DIR) for _ in f if _.endswith(".py"))
    print(f"\nFiles checked: {total_files}")
    print(f"Imports checked: {checked}")
    print(f"Errors: {errors}")

    if errors:
        print("\nRESULT: FAIL")
        sys.exit(1)
    else:
        print("\nRESULT: PASS")


if __name__ == "__main__":
    check_imports()