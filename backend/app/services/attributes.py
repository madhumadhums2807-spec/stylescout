"""Detect category / colour of the uploaded image.

CLIP path (zero-shot): compare the image vector with text vectors such as
"a photo of a red dress". The label whose text is closest wins; softmax turns the raw
similarities into probabilities (the 100 is CLIP's learned "temperature").

Fallback path: no text encoder, so we vote among the nearest catalogue products instead.
"""
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np

from ..schemas import Attribute, DetectedAttributes

# These lists match the vocabulary produced by scripts/import_catalog.py
CATEGORIES = [
    "dress", "t-shirt", "shirt", "top", "tunic", "kurta", "jeans", "trousers", "track pants", "shorts",
    "capris", "leggings", "skirt", "jacket", "sweater", "sweatshirt", "saree", "dupatta", "salwar",
    "flats", "heels", "sandals", "flip flops", "casual shoes", "formal shoes", "sports shoes",
]
COLOURS = [
    "black", "white", "grey", "blue", "navy", "red", "maroon", "pink", "purple", "green", "olive",
    "teal", "yellow", "orange", "brown", "beige", "cream", "gold", "silver",
]

_PROMPTS = {
    "category": [f"a photo of a {c}, a piece of clothing or footwear" for c in CATEGORIES],
    "colour": [f"a photo of a {c} coloured piece of clothing or footwear" for c in COLOURS],
}
_LABELS = {"category": CATEGORIES, "colour": COLOURS}

_text_cache: Dict[str, np.ndarray] = {}


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def _zero_shot(image_vec: np.ndarray, embedder, kind: str) -> Attribute:
    if kind not in _text_cache:  # encode each prompt set once, reuse forever
        _text_cache[kind] = embedder.embed_texts(_PROMPTS[kind])
    logits = 100.0 * (_text_cache[kind] @ image_vec)
    probs = _softmax(logits)
    best = int(probs.argmax())
    return Attribute(label=_LABELS[kind][best], confidence=round(float(probs[best]), 3))


FASHION_PROMPTS = [
    "a photo of clothing", "a photo of a person wearing an outfit",
    "a photo of a pair of shoes", "a photo of a handbag or fashion accessory",
]
NON_FASHION_PROMPTS = [
    "a photo of a landscape or scenery", "a photo of an animal", "a photo of food",
    "a photo of a building or a room", "a photo of a car or vehicle",
    "a screenshot or a document with text", "a photo of plants or flowers",
    "a photo of a gadget or electronic device", "a cartoon or abstract artwork",
]
FASHION_THRESHOLD = 0.5


def fashion_check(image_vec: np.ndarray, embedder):
    """Zero-shot 'is this clothing at all?' test: fashion prompts vs non-fashion prompts.
    Returns (looks_like_fashion, probability_that_it_is_fashion)."""
    if "fashion" not in _text_cache:
        _text_cache["fashion"] = embedder.embed_texts(FASHION_PROMPTS + NON_FASHION_PROMPTS)
    probs = _softmax(100.0 * (_text_cache["fashion"] @ image_vec))
    p_fashion = float(probs[: len(FASHION_PROMPTS)].sum())
    return p_fashion >= FASHION_THRESHOLD, round(p_fashion, 3)


def colour_probabilities(image_vec: np.ndarray, embedder) -> np.ndarray:
    """CLIP's probability for each colour in COLOURS (sums to 1)."""
    if "colour" not in _text_cache:
        _text_cache["colour"] = embedder.embed_texts(_PROMPTS["colour"])
    return _softmax(100.0 * (_text_cache["colour"] @ image_vec))


def detect_with_clip(image_vec: np.ndarray, embedder) -> DetectedAttributes:
    return DetectedAttributes(
        method="clip-zero-shot",
        category=_zero_shot(image_vec, embedder, "category"),
        colour=_zero_shot(image_vec, embedder, "colour"),
    )


def detect_by_neighbours(neighbours: List[dict]) -> DetectedAttributes:
    """neighbours: product dicts with a 'score', best first. Similarity-weighted vote."""

    def vote(field: str) -> Optional[Attribute]:
        weights: Dict[str, float] = defaultdict(float)
        for n in neighbours:
            if n.get(field):
                weights[n[field]] += max(n["score"], 0.0)
        total = sum(weights.values())
        if total == 0:
            return None
        label = max(weights, key=weights.get)
        return Attribute(label=label, confidence=round(weights[label] / total, 3))

    return DetectedAttributes(
        method="neighbour-vote",
        category=vote("category"),
        colour=vote("color"),
    )
