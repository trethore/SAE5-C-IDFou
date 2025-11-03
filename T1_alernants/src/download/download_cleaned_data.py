#!/usr/bin/env python3
import sys
import zipfile
from pathlib import Path

DRIVE_FILE_IDS = [
    "1qPqFtijkDU02qKJdha89gAb-Bogh3bdV",
    "1dvOftvUTdP8GKJ0dQjMIoY0OTpRK_kFe",
]
DRIVE_URLS = [f"https://drive.google.com/uc?id={fid}" for fid in DRIVE_FILE_IDS]


def main():
    try:
        import gdown
    except ImportError:
        print("gdown is not installed. Run: pip install gdown", file=sys.stderr)
        sys.exit(1)

    here = Path(__file__).resolve().parent
    data_dir = (here / "../../cleaned_data").resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    removed = 0
    for csv in data_dir.rglob("*.csv"):
        try:
            csv.unlink()
            removed += 1
        except Exception as e:
            print(f"Warning: couldn't remove {csv}: {e}", file=sys.stderr)

    print(f"Removed {removed} CSV file(s).")

    for idx, url in enumerate(DRIVE_URLS, start=1):
        zip_path = here / f"download_{idx}.zip"
        if zip_path.exists():
            zip_path.unlink()

        print(f"Downloading archive #{idx} from Google Drive...")
        out = gdown.download(url, str(zip_path), quiet=False)
        if not out or not zip_path.exists():
            print(f"Error: download {idx} failed or file missing.", file=sys.stderr)
            continue

        if not zipfile.is_zipfile(zip_path):
            print(f"Error: downloaded file is not a valid ZIP: {zip_path}", file=sys.stderr)
            continue

        print(f"Extracting archive #{idx} to {data_dir}...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(data_dir)

        try:
            zip_path.unlink()
        except Exception:
            pass

    print(f"All archives processed. Extracted into {data_dir}.")


if __name__ == "__main__":
    main()
