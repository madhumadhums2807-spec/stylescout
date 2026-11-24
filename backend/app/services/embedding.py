"""Turns images (and text) into 512-d L2-normalised vectors.

Two implementations share one interface:

* ClipEmbedder     - the real model (openai/clip-vit-base-patch32). Images AND text live in the
                     same vector space, which is what enables zero-shot attribute detection.
* FallbackEmbedder - a tiny hand-made embedder (colour histogram + edge directions + coarse
                     silhouette). It exists so the project still runs offline / without a 600 MB
                     model download (tests, first-day demos). It is NOT as smart as CLIP.

`get_embedder()` picks one according to STYLESCOUT_EMBEDDER (auto | clip | fallback).
"""
import logging
from functools import lru_cache
from typing import List

import cv2
import numpy as np
from PIL import Image

from .. import config

log = logging.getLogger("stylescout.embedding")


def _l2_normalise(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return (x / np.maximum(norms, 1e-12)).astype("float32")


class ClipEmbedder:
    name = "clip-vit-base-patch32"
    supports_text = True

    def __init__(self, model_name: str = config.MODEL_NAME):
        # imported lazily so the server can start (in fallback mode) without torch installed
        import torch
        from transformers import CLIPModel, CLIPProcessor

        self.torch = torch
        log.info("Loading CLIP model %s ...", model_name)
        self.model = CLIPModel.from_pretrained(model_name).eval()
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def _to_array(self, feats) -> np.ndarray:
        if not isinstance(feats, self.torch.Tensor):  # some transformers versions wrap the output
            feats = feats.pooler_output
        return feats.detach().cpu().numpy()

    def embed_images(self, images: List[Image.Image]) -> np.ndarray:
        inputs = self.processor(images=images, return_tensors="pt")
        with self.torch.no_grad():
            feats = self.model.get_image_features(**inputs)
        return _l2_normalise(self._to_array(feats))

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        inputs = self.processor(text=texts, return_tensors="pt", padding=True)
        with self.torch.no_grad():
            feats = self.model.get_text_features(**inputs)
        return _l2_normalise(self._to_array(feats))


class FallbackEmbedder:
    name = "fallback-colour-shape"
    supports_text = False

    def _one(self, img: Image.Image) -> np.ndarray:
        rgb = np.array(img.convert("RGB").resize((96, 96), Image.BILINEAR))
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype("float32")

        # foreground mask: pixels that differ from the border-median background colour
        border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]).astype("float32")
        bg = np.median(border, axis=0)
        dist = np.linalg.norm(rgb.astype("float32") - bg, axis=2)
        fg_mask = (dist > 40).astype("uint8")
        if fg_mask.mean() < 0.03:  # e.g. white item on white backdrop: just use everything
            fg_mask[:] = 1

        # 1) colour histogram of the GARMENT only (12 hue x 3 sat x 3 val = 108)
        hist = cv2.calcHist([hsv], [0, 1, 2], fg_mask, [12, 3, 3], [0, 180, 0, 256, 0, 256]).flatten()
        hist = hist / max(hist.sum(), 1)
        fg_mean = rgb[fg_mask.astype(bool)].mean(axis=0) / 255.0  # average garment colour (3)

        # 2) spatial colour layout: mean RGB on a 4x4 grid (48)
        layout = cv2.resize(rgb, (4, 4), interpolation=cv2.INTER_AREA).astype("float32").flatten() / 255.0

        # 3) edge-direction histogram per 4x4 cell, 8 bins (128) - captures stripes / checks / outlines
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag, ang = cv2.cartToPolar(gx, gy, angleInDegrees=False)
        bins = ((ang % np.pi) / np.pi * 8).astype(int) % 8
        edges = np.zeros((4, 4, 8), dtype="float32")
        cell = 96 // 4
        for i in range(4):
            for j in range(4):
                m = mag[i * cell:(i + 1) * cell, j * cell:(j + 1) * cell].flatten()
                b = bins[i * cell:(i + 1) * cell, j * cell:(j + 1) * cell].flatten()
                edges[i, j] = np.bincount(b, weights=m, minlength=8)
        edges = edges.flatten()
        edges = edges / max(edges.sum(), 1e-6)

        # 4) coarse silhouette: "how far is each pixel from the background colour" on a 12x12 grid (144)
        silhouette = cv2.resize((dist > 40).astype("float32"), (12, 12), interpolation=cv2.INTER_AREA).flatten()

        def unit(v):
            return v / max(np.linalg.norm(v), 1e-6)

        vec = np.concatenate([
            1.0 * unit(hist), 0.8 * fg_mean, 0.4 * unit(layout), 0.8 * unit(edges), 2.6 * unit(silhouette),
        ])
        out = np.zeros(config.EMBED_DIM, dtype="float32")
        out[: len(vec)] = vec
        return out

    def embed_images(self, images: List[Image.Image]) -> np.ndarray:
        return _l2_normalise(np.stack([self._one(i) for i in images]))


@lru_cache(maxsize=1)
def get_embedder():
    mode = config.EMBEDDER_MODE
    if mode == "fallback":
        log.warning("Using FALLBACK embedder (no CLIP). Matches will be rougher.")
        return FallbackEmbedder()
    try:
        return ClipEmbedder()
    except Exception as exc:  # missing torch, no internet for the first download, etc.
        if mode == "clip":
            raise
        log.warning("CLIP could not be loaded (%s). Falling back to the lightweight embedder.", exc)
        return FallbackEmbedder()
