import uuid
from pathlib import Path

from PIL import Image, ImageOps

from app.config import MAX_PHOTO_SIZE, PHOTOS_DIR, THUMB_SIZE, THUMBS_DIR


def save_photo(file_data: bytes, filename: str) -> tuple[str, str]:
    """Save uploaded photo, create thumbnail. Returns (photo_filename, thumb_filename)."""
    ext = Path(filename).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"

    unique_name = f"{uuid.uuid4().hex}{ext}"

    img = Image.open(__import__("io").BytesIO(file_data))
    img = ImageOps.exif_transpose(img)  # Fix rotation from phone cameras
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Save full-size (constrained)
    img.thumbnail((MAX_PHOTO_SIZE, MAX_PHOTO_SIZE), Image.LANCZOS)
    photo_path = PHOTOS_DIR / unique_name
    img.save(photo_path, quality=85, optimize=True)

    # Save thumbnail
    thumb = img.copy()
    thumb.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
    thumb_path = THUMBS_DIR / unique_name
    thumb.save(thumb_path, quality=80, optimize=True)

    return unique_name, unique_name


def delete_photo(photo_filename: str | None, thumb_filename: str | None):
    """Delete photo and thumbnail files."""
    if photo_filename:
        path = PHOTOS_DIR / photo_filename
        path.unlink(missing_ok=True)
    if thumb_filename:
        path = THUMBS_DIR / thumb_filename
        path.unlink(missing_ok=True)
