"""Colour re-ranking.

Why: CLIP image embeddings capture shape and overall style much more strongly than exact colour, so a
blue dress photo can return red dresses of the same cut. We blend in a colour score to fix that.

First attempt (dropped, measured): pick the dominant colour of the photo's pixels with k-means. On this
catalogue it was right for under half the photos, because many pictures show a person (skin, hair) and the
images are tiny, so it added noise. Skin masking and centre-cropping only moved it from ~29% to ~34%.

Current approach: ask CLIP what colour the photo is (zero-shot probability for each of 19 colour names)
and give each product a bonus equal to the probability of ITS colour label (the catalogue's labels are
reliable ground truth), relative to the most likely colour:

    colour_match(product) = P(query is product.colour) / max_colour P(query is colour)      in 0..1
    final_score = (clip_similarity + W * colour_match) / (1 + W)                            stays in 0..1

Products whose colour is not in the zero-shot list (e.g. "multicolour") get a neutral 0.3.
"""
import logging

import numpy as np

from ..models import Product
from .attributes import COLOURS

log = logging.getLogger("stylescout.colour")
UNKNOWN_MATCH = 0.3
_label_index = None  # (n_products,) int: index into COLOURS for each product row, -1 if not in the list


def ensure_features(db) -> None:
    """Map every product (by embedding_index) to its colour label index. Cheap: no image processing."""
    global _label_index
    products = db.query(Product).order_by(Product.embedding_index).all()
    index = np.full(len(products), -1, dtype=int)
    for p in products:
        if p.embedding_index is not None and 0 <= p.embedding_index < len(index) and p.color in COLOURS:
            index[p.embedding_index] = COLOURS.index(p.color)
    _label_index = index
    log.info("Colour labels mapped for %d products (%d outside the zero-shot list).", len(index), int((index < 0).sum()))


def similarities(colour_probs: np.ndarray) -> np.ndarray:
    """Colour match (0..1) of every product for a query whose colour probabilities are given."""
    relative = np.asarray(colour_probs) / max(float(np.max(colour_probs)), 1e-9)
    return np.where(_label_index >= 0, relative[np.clip(_label_index, 0, None)], UNKNOWN_MATCH)
