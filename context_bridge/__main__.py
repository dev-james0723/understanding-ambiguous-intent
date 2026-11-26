"""Owner CLI: python3 -m context_bridge --config FILE OPERATION PROJECT [QUERY]."""
import argparse
import json
import sys

from .core import Bridge, BridgeError, OPERATIONS, candidate_locations, load_config

QUERY_OPS = set(OPERATIONS) - {"discover_memory_sources", "list_memory_sources", "read_memory"}

def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only UAI Context Bridge")
    parser.add_argument("--config", help="owner-controlled local grant configuration")
    subs = parser.add_subparsers(dest="operation", required=True)
    subs.add_parser("suggest", help="metadata-only standard candidate paths; no grants or reads")
    subs.add_parser("serve", help="start optional MCP server over stdio")
    for operation in OPERATIONS:
        sub = subs.add_parser(operation)
        sub.add_argument("project")
        if operation == "read_memory":
            sub.add_argument("record_id")
        elif operation in QUERY_OPS:
            sub.add_argument("query")
            sub.add_argument("--limit", type=int, default=6)
    args = parser.parse_args(argv)
    try:
        if args.operation == "suggest":
            result = {"authorized": False, "candidates": candidate_locations()}
        else:
            if not args.config:
                raise BridgeError("--config is required for all retrieval and server operations")
            bridge = Bridge(load_config(args.config))
            if args.operation == "serve":
                from .mcp_server import serve
                serve(bridge)
                return 0
            kwargs = {"project": args.project}
            if args.operation == "read_memory":
                kwargs["record_id"] = args.record_id
            elif args.operation in QUERY_OPS:
                kwargs.update(query=args.query, limit=args.limit)
            result = getattr(bridge, args.operation)(**kwargs)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except BridgeError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError, RecursionError):
        print('{"status":"error","error":"configuration or local source unavailable or invalid"}', file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
