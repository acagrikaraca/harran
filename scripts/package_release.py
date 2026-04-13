from __future__ import annotations

from datetime import datetime
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

INCLUDE_DIRS = ["app", "bulletins", "database", "matching", "portfolio", "tests", "ui", "ai"]
INCLUDE_FILES = ["README.md", "index.html", ".gitignore"]
EXCLUDE_PARTS = {"__pycache__", ".git", "data", "dist"}
EXCLUDE_SUFFIXES = {".pyc"}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDE_PARTS for part in path.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    return True


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    archive_path = DIST / f"harran_mvp_{stamp}.zip"

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_name in INCLUDE_FILES:
            path = ROOT / file_name
            if path.exists():
                archive.write(path, arcname=file_name)

        for dir_name in INCLUDE_DIRS:
            base = ROOT / dir_name
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if path.is_file() and should_include(path):
                    archive.write(path, arcname=str(path.relative_to(ROOT)))

    print(f"Package ready: {archive_path}")


if __name__ == "__main__":
    main()
