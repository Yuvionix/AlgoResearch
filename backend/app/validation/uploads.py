from __future__ import annotations

import re
from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.config import ALLOWED_EXTENSIONS, MAX_CSV_ROWS, MAX_UPLOAD_MB, UPLOAD_DIR


class UploadError(ValueError):
    pass


def validate_csv_file(file: FileStorage | None) -> bytes:
    if file is None or file.filename is None or file.filename.strip() == "":
        raise UploadError("No file uploaded.")
    filename = secure_filename(file.filename)
    if not filename:
        raise UploadError("Unsafe or empty filename.")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise UploadError("Only .csv files are accepted.")
    content = file.read()
    if not content:
        raise UploadError("Uploaded file is empty.")
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        raise UploadError(f"File exceeds {MAX_UPLOAD_MB} MB limit.")
    if content.count(b"\n") > MAX_CSV_ROWS + 5:
        raise UploadError(f"CSV exceeds {MAX_CSV_ROWS} rows.")
    return content


def safe_store_name(original: str) -> str:
    name = secure_filename(original)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or "upload.csv"


def persist_upload(content: bytes, original: str) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_DIR / safe_store_name(original)
    path.write_bytes(content)
    return path
