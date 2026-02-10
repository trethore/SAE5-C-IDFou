#!/usr/bin/env python3
import sys
from typing import Callable

from download_cleaned_data import main as download_cleaned_data_main
from download_data import main as download_data_main


def _run(label: str, func: Callable[[], None]) -> None:
    print(f"=== {label} ===")
    try:
        func()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        print(f"{label} failed; aborting.", file=sys.stderr)
        raise SystemExit(code) from exc


def main() -> None:
    _run("Downloading raw data", download_data_main)
    _run("Downloading cleaned data", download_cleaned_data_main)
    print("All downloads completed successfully.")


if __name__ == "__main__":
    main()
