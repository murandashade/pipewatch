"""CLI entry point for pipewatch."""
import sys
import argparse
from pathlib import Path

from pipewatch.config import load_config, validate_config
from pipewatch.runner import run_all, summarise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipewatch",
        description="Monitor and alert on ETL pipeline failures.",
    )
    parser.add_argument(
        "-c", "--config",
        default="pipewatch.json",
        metavar="FILE",
        help="Path to config file (default: pipewatch.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and validate config without running pipelines.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress summary output.",
    )
    return parser


def _load_and_validate(config_path: Path):
    """Load and validate config, printing errors to stderr on failure.

    Returns the config object on success, or None on failure.
    """
    try:
        cfg = load_config(config_path)
        validate_config(cfg)
        return cfg
    except FileNotFoundError:
        print(f"[pipewatch] Config file not found: {config_path}", file=sys.stderr)
    except ValueError as exc:
        print(f"[pipewatch] Invalid config: {exc}", file=sys.stderr)
    return None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    cfg = _load_and_validate(config_path)
    if cfg is None:
        return 2

    if args.dry_run:
        print(f"[pipewatch] Config OK — {len(cfg.pipelines)} pipeline(s) defined.")
        return 0

    results = run_all(cfg)
    if not args.quiet:
        print(summarise(results))

    return 0 if all(r.success for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
