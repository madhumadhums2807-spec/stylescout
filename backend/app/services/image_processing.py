"""OpenCV + Pillow preprocessing: decode, normalise colour space, resize, find dominant colour."""
import io
from typing import Tuple

import cv2
import numpy as np
from PIL import Image, ImageOps

from .. import config


def load_image(data: bytes) -> Image.Image:
    """Bytes -> RGB PIL image. exif_transpose fixes phone photos that are stored rotated."""
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        # flatten transparency onto white so transparent PNG backgrounds do not become black
        rgba = img.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        img = Image.alpha_composite(background, rgba)
    return img.convert("RGB")


def resize_max_side(img: Image.Image, max_side: int = config.PREPROCESS_MAX_SIDE) -> Image.Image:
    w, h = img.size
    scale = max_side / max(w, h)
    if scale >= 1:
        return img
    return img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)


def preprocess(data: bytes) -> Image.Image:
    return resize_max_side(load_image(data))


def _name_colour(r: int, g: int, b: int) -> str:
    """Map an RGB value to a simple human colour name using HSV rules."""
    h, s, v = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2HSV)[0][0]
    hue = int(h) * 2  # OpenCV hue is 0-179; convert to degrees 0-358
    sat, val = s / 255.0, v / 255.0

    if val < 0.18:
        return "black"
    if sat < 0.12:
        return "white" if val > 0.85 else "grey"
    if val < 0.5 and 200 <= hue <= 260:
        return "navy"
    if 15 <= hue < 50 and sat < 0.45 and val > 0.7:
        return "beige"
    if 10 <= hue < 45 and val < 0.6:
        return "brown"
    if hue < 12 or hue >= 345:
        return "red"
    if hue < 40:
        return "orange"
    if hue < 70:
        return "yellow"
    if hue < 165:
        return "green"
    if hue < 200:
        return "teal"
    if hue < 255:
        return "blue"
    if hue < 295:
        return "purple"
    return "pink"


def dominant_rgb(img: Image.Image, k: int = 4) -> Tuple[int, int, int]:
    """k-means on a small copy of the image; returns the RGB of the biggest non-background cluster."""
    grid = np.array(img.resize((64, 64), Image.BILINEAR), dtype=np.float32)
    small = grid.reshape(-1, 3)

    # Background guess: the median colour of the image border (product photos usually have a
    # plain backdrop). Pixels close to it are ignored, unless that would leave almost nothing.
    border = np.concatenate([grid[0], grid[-1], grid[:, 0], grid[:, -1]])
    background = np.median(border, axis=0)
    distance = np.linalg.norm(small - background, axis=1)
    foreground = small[distance > 35]
    pixels = foreground if len(foreground) > 50 else small

    k = min(k, len(pixels))
    cv2.setRNGSeed(0)  # same image -> same answer every time
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centres = cv2.kmeans(pixels, k, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
    biggest = np.bincount(labels.flatten()).argmax()
    r, g, b = (int(round(c)) for c in centres[biggest])
    return r, g, b


def dominant_colour(img: Image.Image, k: int = 4) -> Tuple[str, str]:
    """(name, hex) of the dominant colour, for display."""
    r, g, b = dominant_rgb(img, k)
    return _name_colour(r, g, b), f"#{r:02x}{g:02x}{b:02x}"
