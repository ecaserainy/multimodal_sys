import os
import uuid
from pathlib import Path

BASE_UPLOAD_DIR = Path("temp_uploads")

def ensure_upload_dir():
    if not BASE_UPLOAD_DIR.exists():
        BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload_file(upload_file) -> str:
    ensure_upload_dir()
    suffix = Path(upload_file.filename).suffix
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    file_path = BASE_UPLOAD_DIR / unique_name

    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())

    return str(file_path)

def remove_file(file_path: str):
    try:
        os.remove(file_path)
    except Exception:
        pass
