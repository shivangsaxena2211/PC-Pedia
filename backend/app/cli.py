"""PC Pedia command-line interface."""

import argparse
import json
import logging
import sys

from app import create_app
from app import db
from app.services.import_service import import_hardware_from_path
from app.services.product_reconciliation_service import reconcile_legacy_cpu_slugs


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
        f"\nSummary: files={result.get('files_processed', 1)} "
        f"total={result['total']} created={result['created']} "
        f"updated={result['updated']} skipped={result['skipped']} "
        f"errors={result['errors']} warnings={result['warnings']}"
    )
    if result.get("dry_run"):
        print(
            f"Dry run: valid={result.get('valid_records', 0)} "
            f"invalid={result.get('invalid_records', 0)} "
            f"new={result.get('new_records', 0)} "
            f"existing={result.get('existing_records', 0)}"
        )
        print("Dry run complete — no database changes were committed.")


def cmd_reconcile_cpus(args) -> int:
    app = create_app()
    with app.app_context():
        result = reconcile_legacy_cpu_slugs(dry_run=args.dry_run)
        print(
            f"Reconciliation: merged={result.merged} renamed={result.renamed} "
            f"skipped={result.skipped} errors={len(result.errors)}"
        )
        for action in result.actions:
            print(f"  {action}")
        for error in result.errors:
            print(f"  ERROR: {error}", file=sys.stderr)
        if args.dry_run:
            db.session.rollback()
        return 1 if result.errors else 0


def cmd_import_data(args) -> int:
    app = create_app()
    with app.app_context():
        result = import_hardware_from_path(
            args.path,
            mode=args.mode,
            dry_run=args.dry_run,
            replace_specifications=args.replace_specifications,
            replace_images=args.replace_images,
        )
        if result.total == 0:
            print("No records found in import path.", file=sys.stderr)
            return 1
        _print_result(result.to_dict())
        return 1 if result.errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PC Pedia management CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

    subparsers = parser.add_subparsers(dest="command", required=True)

    import_parser = subparsers.add_parser(
        "import-data",
        help="Import hardware records from JSON, CSV, or a directory",
    )
    import_parser.add_argument(
        "path",
        help="Path to JSON/CSV file or directory containing import files",
    )
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

    reconcile_parser = subparsers.add_parser(
        "reconcile-cpus",
        help="Merge legacy seed CPU slugs into canonical catalog slugs",
    )
    reconcile_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview reconciliation without modifying the database",
    )
    reconcile_parser.set_defaults(func=cmd_reconcile_cpus)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
