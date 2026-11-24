#!/usr/bin/env python3
"""Install only the runtime skill, with no overwrite and no network access."""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

NAME = "understanding-ambiguous-intent"
ROOT = Path(__file__).resolve().parents[1]


def install(target, source=None, dry_run=False):
    source = Path(source) if source is not None else ROOT / "skills" / NAME
    target = Path(target).expanduser().absolute()
    destination = target / NAME
    if not (source / "SKILL.md").is_file():
        raise ValueError("Source is missing SKILL.md")
    for item in source.rglob("*"):
        if item.is_symlink():
            raise ValueError("Runtime source must not contain symlinks")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("UAI already exists at destination; review and back it up before installing")
    if dry_run:
        return {"action": "dry-run", "destination": str(destination), "written": False}
    target.mkdir(parents=True, exist_ok=True)
    # Reserve the exact directory atomically, so concurrent installers cannot overwrite it.
    destination.mkdir()
    try:
        for item in source.iterdir():
            if item.is_dir():
                shutil.copytree(item, destination / item.name)
            else:
                shutil.copy2(item, destination / item.name)
    except BaseException:
        shutil.rmtree(destination)
        raise
    return {"action": "installed", "destination": str(destination), "written": True,
            "scope": "runtime-files-only", "host_loading_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True, help="Host's skills parent directory")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.target, dry_run=args.dry_run), ensure_ascii=False))
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
