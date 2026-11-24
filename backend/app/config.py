"""Central settings. Everything tunable lives here so the rest of the code has no magic numbers."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("STYLESCOUT_DATA_DIR", BASE_DIR / "data"))
IMAGES_DIR = DATA_DIR / "images"
PRODUCTS_JSON = DATA_DIR / "products.json"
DB_URL = os.getenv("STYLESCOUT_DB_URL", f"sqlite:///{DATA_DIR / 'stylescout.db'}")
FAISS_PATH = DATA_DIR / "faiss.index"
FAISS_META_PATH = DATA_DIR / "faiss.meta.json"

# --- AI model ---------------------------------------------------------------
MODEL_NAME = os.getenv("CLIP_MODEL", "openai/clip-vit-base-patch32")
# "auto"     -> try CLIP, fall back to the lightweight colour/shape embedder if CLIP cannot load
# "clip"     -> CLIP only (fail loudly if it cannot load)
# "fallback" -> never load CLIP (fast, used by tests and offline demos)
EMBEDDER_MODE = os.getenv("STYLESCOUT_EMBEDDER", "auto").lower()
EMBED_DIM = 512  # CLIP ViT-B/32 output size; the fallback embedder is padded to the same size

# --- Upload validation ------------------------------------------------------
MAX_UPLOAD_MB = 5
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MIN_IMAGE_SIDE = 32  # pixels
PREPROCESS_MAX_SIDE = 512  # images are shrunk to this before analysis

# --- Search -----------------------------------------------------------------
DEFAULT_TOP_K = 60
MAX_TOP_K = 200
NEIGHBOURS_FOR_ATTRIBUTES = 5  # used only by the fallback embedder

# Colour re-ranking: final = (clip_similarity + W * colour_match) / (1 + W)
# W = 0 turns it off. Use `python -m scripts.evaluate` to pick the best W for your data.
COLOUR_WEIGHT = float(os.getenv("STYLESCOUT_COLOUR_WEIGHT", "0.03"))

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
