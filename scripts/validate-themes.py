#!/usr/bin/env python3
"""Validate the theme set.

Checks that every theme registered in package.json exists and parses, and
that all variants are structurally identical: the same workbench color keys,
the same token rules (names and scopes, in the same order), and the same
semantic token keys. Only the color values may differ between variants.

Usage: python3 scripts/validate-themes.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEX = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")


def load_jsonc(path: Path) -> dict:
    text = re.sub(r"^\s*//.*$", "", path.read_text(), flags=re.M)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


def token_signature(theme: dict) -> list:
    sig = []
    for rule in theme["tokenColors"]:
        scope = rule.get("scope")
        scope = tuple(scope) if isinstance(scope, list) else scope
        sig.append((rule.get("name"), scope))
    return sig


def check_hex_values(name: str, theme: dict, errors: list) -> None:
    for key, value in theme["colors"].items():
        if not HEX.match(value):
            errors.append(f"{name}: colors[{key}] is not a hex color: {value}")


def main() -> int:
    manifest = json.loads((ROOT / "package.json").read_text())
    contributions = manifest["contributes"]["themes"]
    errors = []
    themes = []

    for contribution in contributions:
        path = ROOT / contribution["path"]
        if not path.is_file():
            errors.append(f"{contribution['label']}: missing file {path}")
            continue
        try:
            theme = load_jsonc(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: parse error: {exc}")
            continue
        if theme.get("name") != contribution["label"]:
            errors.append(
                f"{path.name}: name {theme.get('name')!r} != label {contribution['label']!r}"
            )
        if theme.get("type") != "dark":
            errors.append(f"{path.name}: type is not dark")
        if theme.get("semanticHighlighting") is not True:
            errors.append(f"{path.name}: semanticHighlighting is not true")
        check_hex_values(path.name, theme, errors)
        themes.append((path.name, theme))

    if len(themes) > 1:
        ref_name, ref = themes[0]
        for name, theme in themes[1:]:
            if set(theme["colors"]) != set(ref["colors"]):
                diff = sorted(set(theme["colors"]) ^ set(ref["colors"]))
                errors.append(f"{name}: colors keys differ from {ref_name}: {diff[:10]}")
            if token_signature(theme) != token_signature(ref):
                errors.append(f"{name}: tokenColors names/scopes differ from {ref_name}")
            if set(theme["semanticTokenColors"]) != set(ref["semanticTokenColors"]):
                errors.append(f"{name}: semanticTokenColors keys differ from {ref_name}")

    if errors:
        print("\n".join(errors))
        return 1

    name, ref = themes[0]
    print(
        f"{len(themes)} themes OK — {len(ref['colors'])} colors, "
        f"{len(ref['tokenColors'])} token rules, "
        f"{len(ref['semanticTokenColors'])} semantic keys, identical across variants"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
