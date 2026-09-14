"""PC Pedia command-line interface."""

import argparse
import json
import logging
import sys

from app import create_app
from app.services.import_service import HardwareImportService, import_hardware


def _configure_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
    )
    logging.getLogger("pc_pedia.import").setLevel(level)


def _print_result(result: dict):
    print(json.dumps(result, indent=2))
    print(
        f"\nSummary: total={result['total']} created={result['created']} "
        f"updated={result['updated']} skipped={result['skipped']} "
        f"errors={result['errors']} warnings={result['warnings']}"
    )
    if result.get("dry_run"):
        print("Dry run complete — no database changes were committed.")


def cmd_import_data(args) -> int:
    app = create_app()
    with app.app_context():
        records = HardwareImportService.load_records_from_file(args.path)
        if not records:
            print("No records found in import file.", file=sys.stderr)
            return 1

        result = import_hardware(
            records,
            mode=args.mode,
            dry_run=args.dry_run,
            replace_specifications=args.replace_specifications,
            replace_images=args.replace_images,
        )
        _print_result(result.to_dict())
        return 1 if result.errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PC Pedia management CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

    subparsers = parser.add_subparsers(dest="command", required=True)

    import_parser = subparsers.add_parser(
        "import-data",
        help="Import hardware records from JSON or CSV",
    )
    import_parser.add_argument("path", help="Path to JSON or CSV import file")
    import_parser.add_argument(
        "--mode",
        choices=["create", "update", "upsert"],
        default="upsert",
        help="Import mode (default: upsert)",
    )
    import_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and preview without modifying the database",
    )
    import_parser.add_argument(
        "--replace-specifications",
        action="store_true",
        help="Replace all specifications for updated products",
    )
    import_parser.add_argument(
        "--replace-images",
        action="store_true",
        help="Replace all images for updated products",
    )
    import_parser.set_defaults(func=cmd_import_data)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
