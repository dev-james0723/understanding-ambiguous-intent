#!/usr/bin/env python3
"""Create one explicit local source grant without reading memory contents."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from context_bridge.core import ADAPTERS, Bridge, BridgeError


def configure(output, root, project, adapter, files=(), include_instructions=False,
              personal=False, source_id="memory"):
    config = {"schema_version": 1, "user": "local-user", "workspace": "local-work",
              "project": project, "sources": [{"id": source_id, "adapter": adapter,
                  "root": str(Path(root).expanduser().absolute()),
                  "scope": "personal" if personal else "project:" + project}]}
    grant = config["sources"][0]
    if files:
        grant["files"] = list(files)
    if include_instructions:
        grant["include_instruction_context"] = True
    bridge = Bridge(config)
    availability = bridge.discover_memory_sources(project)
    if not availability["records"][0]["available"]:
        raise BridgeError("selected source root is unavailable")
    # Bind the persisted grant to the directory just checked, not a mutable alias.
    grant["root"] = str(bridge.sources[0].root)
    destination = Path(output).expanduser().absolute()
    if destination.resolve().is_relative_to(ROOT.resolve()):
        raise BridgeError("keep private source grants outside the UAI checkout")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    descriptor = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return {"status": "configured", "config": str(destination), "project": project,
            "source_id": source_id, "adapter": adapter,
            "memory_content_read": False, "host_registered": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Project identifier used in bridge calls")
    parser.add_argument("--root", required=True, type=Path, help="Exact source directory to grant")
    parser.add_argument("--adapter", required=True, choices=sorted(ADAPTERS))
    parser.add_argument("--out", required=True, type=Path, help="New private config file outside this checkout")
    parser.add_argument("--source-id", default="memory")
    parser.add_argument("--file", action="append", default=[], help="Exact relative file for custom adapter; repeat as needed")
    parser.add_argument("--include-instruction-context", action="store_true")
    parser.add_argument("--personal", action="store_true", help="Grant this personal source to the configured project")
    args = parser.parse_args()
    try:
        result = configure(args.out, args.root, args.project, args.adapter, args.file,
                           args.include_instruction_context, args.personal, args.source_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except FileExistsError:
        parser.exit(2, "Configuration already exists; review it instead of overwriting.\n")
    except (BridgeError, OSError, ValueError) as exc:
        message = str(exc) if isinstance(exc, BridgeError) else "Could not create private configuration."
        parser.exit(2, message + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
