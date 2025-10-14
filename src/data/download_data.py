#!/usr/bin/env python3
import sys
import zipfile
from pathlib import Path

DRIVE_FILE_ID = "1S4KMI-bBA0b3BEi_D-PW5qtPc_UdEl4T"
DRIVE_URL = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"

def main():
    try:
        import gdown
    except ImportError:
        print("gdown is not installed. Run: pip install gdown", file=sys.stderr)
        sys.exit(1)

    here = Path(__file__).resolve().parent
    data_dir = (here / "../../data").resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    removed = 0
    for csv in data_dir.rglob("*.csv"):
        try:
            csv.unlink()
            removed += 1
        except Exception as e:
            print(f"Warning: couldn't remove {csv}: {e}", file=sys.stderr)

    zip_path = here / "download.zip"
    if zip_path.exists():
        zip_path.unlink()

    print("Downloading ZIP from Google Drive...")
    out = gdown.download(DRIVE_URL, str(zip_path), quiet=False)
    if not out or not zip_path.exists():
        print("Error: download failed or file missing.", file=sys.stderr)
        sys.exit(2)

    if not zipfile.is_zipfile(zip_path):
        print(f"Error: downloaded file is not a valid ZIP: {zip_path}", file=sys.stderr)
        sys.exit(3)

    print(f"Extracting to {data_dir}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(data_dir)

    try:
        zip_path.unlink()
    except Exception:
        pass

    print(f"Done. Removed {removed} CSV file(s), downloaded and extracted archive into {data_dir}.")

if __name__ == "__main__":
    main()