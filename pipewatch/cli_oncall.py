import argparse
from pipewatch.oncall import set_oncall, get_oncall, remove_oncall, format_oncall_text

_DEFAULT_FILE = "pipewatch_oncall.json"


def _add_subcommands(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("oncall", help="Manage on-call contacts for pipelines")
    s = p.add_subparsers(dest="oncall_cmd", required=True)

    add = s.add_parser("set", help="Set on-call contact for a pipeline")
    add.add_argument("pipeline", help="Pipeline name")
    add.add_argument("contact", help="Contact name or email")
    add.add_argument("--file", default=_DEFAULT_FILE)

    show = s.add_parser("show", help="Show on-call contact for a pipeline")
    show.add_argument("pipeline", help="Pipeline name")
    show.add_argument("--file", default=_DEFAULT_FILE)

    rm = s.add_parser("remove", help="Remove on-call contact for a pipeline")
    rm.add_argument("pipeline", help="Pipeline name")
    rm.add_argument("--file", default=_DEFAULT_FILE)

    ls = s.add_parser("list", help="List all on-call contacts")
    ls.add_argument("--file", default=_DEFAULT_FILE)


def handle_oncall(args) -> int:
    if args.oncall_cmd == "set":
        set_oncall(args.pipeline, args.contact, path=args.file)
        print(f"On-call for '{args.pipeline}' set to '{args.contact}'.")
        return 0

    if args.oncall_cmd == "show":
        contacts = get_oncall(args.pipeline, path=args.file)
        if not contacts:
            print(f"No on-call contact set for '{args.pipeline}'.")
        else:
            for c in contacts:
                print(format_oncall_text(c))
        return 0

    if args.oncall_cmd == "remove":
        removed = remove_oncall(args.pipeline, path=args.file)
        if removed:
            print(f"Removed on-call contact for '{args.pipeline}'.")
        else:
            print(f"No on-call contact found for '{args.pipeline}'.")
        return 0

    if args.oncall_cmd == "list":
        from pipewatch.oncall import _load
        data = _load(args.file)
        if not data:
            print("No on-call contacts configured.")
            return 0
        for pipeline, contacts in data.items():
            print(f"{pipeline}:")
            for c in contacts:
                print(f"  {format_oncall_text(c)}")
        return 0

    return 1
