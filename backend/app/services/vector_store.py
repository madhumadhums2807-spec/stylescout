"""FAISS wrapper: build / save / load / search.

IndexFlatIP = exact brute-force inner-product search. Because every vector is L2-normalised,
inner product == cosine similarity. Row i of the index is the product whose
`embedding_index` is i.

A small meta file records WHICH embedder built the index. Vectors from different models are
not comparable, so if the configured embedder changes we rebuild automatically.
"""
import json
import logging
from typing import List, Tuple

import faiss
import numpy as np
from PIL import Image

from .. import config
from ..models import Product

log = logging.getLogger("stylescout.vector_store")


class VectorStore:
    def __init__(self):
        self.index = None
        self.meta = {}

    @property
    def size(self) -> int:
        return 0 if self.index is None else self.index.ntotal

    def build(self, vectors: np.ndarray, embedder_name: str):
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(np.ascontiguousarray(vectors, dtype="float32"))
        self.index = index
        self.meta = {"embedder": embedder_name, "count": int(vectors.shape[0]), "dim": int(vectors.shape[1])}

    def save(self):
        faiss.write_index(self.index, str(config.FAISS_PATH))
        config.FAISS_META_PATH.write_text(json.dumps(self.meta))

    def load(self) -> bool:
        if not (config.FAISS_PATH.exists() and config.FAISS_META_PATH.exists()):
            return False
        self.index = faiss.read_index(str(config.FAISS_PATH))
        self.meta = json.loads(config.FAISS_META_PATH.read_text())
        return True

    def search(self, vector: np.ndarray, k: int) -> Tuple[List[int], List[float]]:
        k = max(1, min(k, self.size))
        scores, ids = self.index.search(np.ascontiguousarray(vector.reshape(1, -1), dtype="float32"), k)
        return ids[0].tolist(), scores[0].tolist()


store = VectorStore()


def _image_path(product: Product):
    return config.IMAGES_DIR / product.image_url.rsplit("/", 1)[-1]


def ensure_index(db, embedder, batch_size: int = 16) -> None:
    """Load the saved index if it matches; otherwise embed every product image and rebuild."""
    products = db.query(Product).order_by(Product.id).all()
    if store.load() and store.meta.get("embedder") == embedder.name and store.meta.get("count") == len(products):
        log.info("Loaded FAISS index (%d vectors, %s).", store.size, embedder.name)
        return

    log.info("Building FAISS index for %d products with %s ...", len(products), embedder.name)
    vectors = []
    for start in range(0, len(products), batch_size):
        batch = products[start:start + batch_size]
        images = [Image.open(_image_path(p)).convert("RGB") for p in batch]
        vectors.append(embedder.embed_images(images))
    matrix = np.vstack(vectors)

    for i, product in enumerate(products):
        product.embedding_index = i
    db.commit()

    store.build(matrix, embedder.name)
    store.save()
    log.info("FAISS index saved.")
