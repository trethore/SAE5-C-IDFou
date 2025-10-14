from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

from globalrules import DEFAULT_DATA_DIR, DEFAULT_OUTPUT_DIR, get_rule_for
from validation import clean_csv, CleanReport


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean raw CSV exports by applying schema-specific rules."
    )
    parser.add_argument(
        "--csv",
        metavar="FILENAME",
        nargs="+",
        help="Specific CSV file names (relative to the data directory) to clean. "
        "Defaults to every *.csv file when omitted.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Directory containing raw CSV files (default: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory where cleaned CSV files are written (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display rule failure statistics for each processed CSV.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of rows processed for each CSV (useful for quick checks).",
    )
    return parser


def _collect_targets(csv_names: Iterable[str] | None, data_dir: Path) -> list[Path]:
    if csv_names:
        targets: list[Path] = []
        for name in csv_names:
            candidate = (data_dir / name).resolve()
            if not candidate.exists():
                print(f"[WARN] Skipping {name!r}: file not found under {data_dir}.")
                continue
            if candidate.suffix.lower() != ".csv":
                print(f"[WARN] Skipping {candidate.name}: not a CSV file.")
                continue
            targets.append(candidate)
        return targets

    return sorted(data_dir.glob("*.csv"))


def _print_report(report: CleanReport, show_stats: bool) -> None:
    if report.skipped:
        print(
            f"[SKIP] {report.csv_name}: {report.messages[0] if report.messages else 'no matching columns'}"
        )
        return

    summary = (
        f"[OK] {report.csv_name}: {report.cleaned_rows}/{report.filtered_rows} rows kept "
        f"({report.retention_percentage:.2f}%); output -> {report.output_path}"
    )
    print(summary)

    for message in report.messages:
        print(f"       {message}")

    if show_stats and report.rule_failures:
        print("       Rule failure counts:")
        for rule_key, failure_count in sorted(
            report.rule_failures.items(), key=lambda item: item[1], reverse=True
        ):
            print(f"         - {rule_key}: {failure_count}")

    if show_stats and report.applied_standardisations:
        print("       Standardisation applied:")
        for column, rule_names in sorted(report.applied_standardisations.items()):
            rule_list = ", ".join(rule_names)
            print(f"         - {column}: {rule_list}")


def run(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    data_dir: Path = args.data_dir.resolve()
    output_dir: Path = args.output_dir.resolve()

    if not data_dir.exists():
        print(f"[ERROR] Data directory {data_dir} does not exist.")
        return 1

    targets = _collect_targets(args.csv, data_dir)

    if not targets:
        print("[WARN] No CSV files matched the provided criteria.")
        return 0

    exit_code = 0

    for csv_path in targets:
        csv_name = csv_path.name
        rule_config = get_rule_for(csv_name)

        if not rule_config:
            print(
                f"[WARN] No rules defined for {csv_name}. "
                "Add a configuration entry in globalrules.py to enable cleaning."
            )
            continue

        report = clean_csv(csv_path, dict(rule_config), output_dir, limit=args.limit)
        _print_report(report, args.stats)

    return exit_code


def main() -> int:
    return run()


if __name__ == "__main__":
    sys.exit(main())
