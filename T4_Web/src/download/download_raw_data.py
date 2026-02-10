#!/usr/bin/env python3
import sys
import zipfile
from pathlib import Path

RAW_DATA_DRIVE_FILE_ID = "1S4KMI-bBA0b3BEi_D-PW5qtPc_UdEl4T"
RAW_DATA_DRIVE_URL = f"https://drive.google.com/uc?id={RAW_DATA_DRIVE_FILE_ID}"


def main() -> None:
    try:
        import gdown
    except ImportError:
        print("gdown is not installed. Run: pip install gdown", file=sys.stderr)
        sys.exit(1)

    here = Path(__file__).resolve().parent
    project_root = Path(__file__).resolve().parents[2]
    data_dir = (project_root / "data/raw_data").resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    removed = 0
    for csv_file in data_dir.rglob("*.csv"):
        try:
            csv_file.unlink()
            removed += 1
        except OSError as exc:
            print(f"Warning: could not remove {csv_file}: {exc}", file=sys.stderr)

    zip_path = here / "download.zip"
    if zip_path.exists():
        zip_path.unlink()

    print("Downloading data ZIP from Google Drive...")
    out = gdown.download(RAW_DATA_DRIVE_URL, str(zip_path), quiet=False)
    if not out or not zip_path.exists():
        print("Error: download failed or file missing.", file=sys.stderr)
        sys.exit(2)

    if not zipfile.is_zipfile(zip_path):
        print(f"Error: downloaded file is not a valid ZIP: {zip_path}", file=sys.stderr)
        sys.exit(3)

    print(f"Extracting archive into {data_dir}...")
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(data_dir)

    try:
        zip_path.unlink()
    except OSError:
        pass

    print(
        f"Done. Removed {removed} CSV file(s) and extracted new data into {data_dir}."
    )


if __name__ == "__main__":
    main()
