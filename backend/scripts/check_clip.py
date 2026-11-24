"""First-run check for the REAL CLIP model (needs internet once, ~600 MB download).
Run from backend/:   python -m scripts.check_clip

It loads CLIP, embeds a sample photo, runs zero-shot attribute detection and prints the result,
so you know the AI path works before demo day."""
from pathlib import Path

from app import config
from app.services import attributes, image_processing
from app.services.embedding import ClipEmbedder

sample = sorted((config.DATA_DIR / "sample_queries").glob("*.jpg"))[0]
print("Loading CLIP (first run downloads the model)...")
embedder = ClipEmbedder()
image = image_processing.preprocess(sample.read_bytes())
vec = embedder.embed_images([image])[0]
print("Embedding shape:", vec.shape, "| L2 norm:", round(float((vec ** 2).sum() ** 0.5), 4))
detected = attributes.detect_with_clip(vec, embedder)
print("Sample:", sample.name)
print("Detected:", detected.category, detected.colour, sep="\n  ")
print("CLIP works.")
