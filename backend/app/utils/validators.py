"""Upload validation. Never trust the filename or the Content-Type header alone:
we also try to decode the bytes with Pillow to prove it is a real image."""
import io
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from .. import config


async def read_and_validate_image(file: UploadFile) -> bytes:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(415, f"Unsupported file type '{ext}'. Use JPG, JPEG, PNG or WEBP.")
    if file.content_type not in config.ALLOWED_MIME_TYPES:
        raise HTTPException(415, f"Unsupported content type '{file.content_type}'.")

    limit = config.MAX_UPLOAD_MB * 1024 * 1024
    data = await file.read(limit + 1)  # read one byte past the limit to detect oversize
    if len(data) == 0:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > limit:
        raise HTTPException(413, f"Image is larger than {config.MAX_UPLOAD_MB} MB.")

    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()  # checks file integrity without fully decoding
        with Image.open(io.BytesIO(data)) as img:
            width, height = img.size
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise HTTPException(400, "File is not a valid image.")

    if min(width, height) < config.MIN_IMAGE_SIDE:
        raise HTTPException(400, f"Image is too small (minimum {config.MIN_IMAGE_SIDE}px per side).")
    return data
