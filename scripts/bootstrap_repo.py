"""Replace repository-owner placeholders before the first public commit."""

from __future__ import annotations

import argparse
from pathlib import Path

TEXT_SUFFIXES = {
    "",
    ".cff",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_DIRECTORIES = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "build", "dist"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github", required=True, help="GitHub username or organization")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    return parser.parse_args()


def replace_placeholders(root: Path, github: str) -> list[Path]:
    if not github or any(character.isspace() for character in github):
        raise ValueError("GitHub username must be non-empty and contain no whitespace")

    changed: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRECTORIES for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            ".gitignore",
            ".editorconfig",
            "Makefile",
            "LICENSE",
        }:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = original.replace("YOUR_GITHUB_USERNAME", github)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.relative_to(root))
    return changed


def main() -> int:
    args = parse_args()
    changed = replace_placeholders(args.root, args.github)
    if not changed:
        print("No placeholders found.")
        return 0
    print("Updated:")
    for path in changed:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
