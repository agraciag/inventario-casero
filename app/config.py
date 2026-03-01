import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
PHOTOS_DIR = UPLOADS_DIR / "photos"
THUMBS_DIR = UPLOADS_DIR / "thumbs"

DATABASE_URL = f"sqlite:///{DATA_DIR / 'inventario.db'}"

SECRET_KEY = os.environ.get("SECRET_KEY", "cambiar-en-produccion-inventario-2026")

# Photo settings
MAX_PHOTO_SIZE = 1200  # px
THUMB_SIZE = 300  # px

# Ensure directories exist
for d in [DATA_DIR, PHOTOS_DIR, THUMBS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
