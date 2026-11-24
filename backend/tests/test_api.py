"""API tests. They run with the lightweight fallback embedder so no model download is needed:
    STYLESCOUT_EMBEDDER=fallback pytest -q
"""
import io
import os

os.environ.setdefault("STYLESCOUT_EMBEDDER", "fallback")

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import config
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # the `with` block runs startup (seed + index build)
        yield c


def _png_bytes(size=(64, 64), colour=(200, 30, 30)):
    buf = io.BytesIO()
    Image.new("RGB", size, colour).save(buf, format="PNG")
    return buf.getvalue()


def _search(client, filename="q.png", data=None, content_type="image/png", **form):
    data = data if data is not None else _png_bytes()
    return client.post("/api/search", files={"file": (filename, data, content_type)}, data=form)


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["products"] == body["index_vectors"] > 0


def test_products_list_and_filters(client):
    r = client.get("/api/products", params={"category": "dress", "max_price": 2000, "limit": 100})
    assert r.status_code == 200
    items = r.json()
    assert items and all(p["category"] == "dress" and p["price"] <= 2000 for p in items)
    assert all(p["is_demo"] is True for p in items)


def _some_ids(client, n):
    return [p["id"] for p in client.get("/api/products", params={"limit": n}).json()]


def test_product_detail_and_404(client):
    pid = _some_ids(client, 1)[0]
    assert client.get(f"/api/products/{pid}").status_code == 200
    assert client.get("/api/products/999999999").status_code == 404


def test_platforms(client):
    platforms = client.get("/api/platforms").json()
    assert set(platforms) == {"Myntra", "Ajio", "Meesho"}


def test_search_finds_the_exact_product(client):
    """Querying with a catalogue image must return that very product first, ~100% match."""
    product = client.get("/api/products/" + str(_some_ids(client, 5)[-1])).json()
    image_path = config.IMAGES_DIR / product["image_url"].rsplit("/", 1)[-1]
    r = _search(client, image_path.name, image_path.read_bytes())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["results"][0]["id"] == product["id"]
    assert body["results"][0]["match_percent"] >= 99
    assert "looks_like_fashion" in body  # None with the fallback embedder, True/False with CLIP
    scores = [x["score"] for x in body["results"]]
    assert scores == sorted(scores, reverse=True)


def test_search_price_and_platform_filters(client):
    r = _search(client, min_price=500, max_price=1500, platforms="Ajio,Myntra", sort="price_asc")
    assert r.status_code == 200
    body = r.json()
    assert body["total_after_filters"] <= body["total_retrieved"]
    prices = [p["price"] for p in body["results"]]
    assert prices == sorted(prices)
    assert all(500 <= p["price"] <= 1500 and p["platform"] in ("Ajio", "Myntra") for p in body["results"])


def test_search_rejects_bad_uploads(client):
    assert _search(client, "x.gif", content_type="image/gif").status_code == 415
    assert _search(client, "x.png", data=b"not an image at all").status_code == 400
    assert _search(client, "x.png", data=b"").status_code == 400
    assert _search(client, "tiny.png", data=_png_bytes((8, 8))).status_code == 400
    too_big = b"\0" * (config.MAX_UPLOAD_MB * 1024 * 1024 + 10)
    assert _search(client, "big.png", data=too_big).status_code == 413
    assert _search(client, min_price=900, max_price=100).status_code == 422


def test_colour_weight_validation(client):
    assert _search(client, colour_weight="-1").status_code == 422
    assert _search(client, colour_weight="9").status_code == 422
    # the fallback embedder has no text encoder, so re-ranking is reported as not applied (weight 0)
    assert _search(client, colour_weight="0.3").json()["colour_weight"] == 0.0


def test_colour_rerank_unit():
    """similarities(): the most likely colour scores 1, others proportionally, unknown colours 0.3."""
    import numpy as np
    from app.services import attributes, colour_rerank

    colour_rerank._label_index = np.array([attributes.COLOURS.index("red"), attributes.COLOURS.index("blue"), -1])
    probs = np.zeros(len(attributes.COLOURS))
    probs[attributes.COLOURS.index("red")] = 0.6
    probs[attributes.COLOURS.index("blue")] = 0.3
    sims = colour_rerank.similarities(probs)
    assert list(np.round(sims, 2)) == [1.0, 0.5, 0.3]


def test_colour_rerank_endpoint_with_text_embedder(client, monkeypatch):
    """Run the whole search with a fake text-capable embedder to exercise the re-ranking path."""
    import numpy as np
    from app.routers import search as search_router
    from app.services import attributes, colour_rerank
    from app.services.embedding import FallbackEmbedder
    from app.main import SessionLocal

    class FakeClip(FallbackEmbedder):
        name = "fallback-colour-shape"  # same name -> same vectors as the saved index
        supports_text = True

        def embed_texts(self, texts):
            v = np.random.default_rng(1).normal(size=(len(texts), 512)).astype("float32")
            return v / np.linalg.norm(v, axis=1, keepdims=True)

    with SessionLocal() as db:
        colour_rerank.ensure_features(db)  # re-map labels (the unit test above replaced the mapping)
    attributes._text_cache.clear()
    monkeypatch.setattr(search_router, "get_embedder", lambda: FakeClip())
    product = client.get("/api/products/" + str(_some_ids(client, 5)[-1])).json()
    image_path = config.IMAGES_DIR / product["image_url"].rsplit("/", 1)[-1]
    body = _search(client, image_path.name, image_path.read_bytes(), colour_weight="0.5").json()
    attributes._text_cache.clear()
    assert body["colour_weight"] == 0.5
    scores = [x["score"] for x in body["results"]]
    assert scores == sorted(scores, reverse=True) and max(scores) <= 1.0
    assert body["looks_like_fashion"] in (True, False)


def test_similar_products(client):
    pid = _some_ids(client, 10)[-1]
    product = client.get(f"/api/products/{pid}").json()
    r = client.get(f"/api/products/{pid}/similar", params={"limit": 8})
    assert r.status_code == 200
    items = r.json()
    assert 0 < len(items) <= 8
    assert all(i["id"] != pid and i["category"] == product["category"] for i in items)
    scores = [i["score"] for i in items]
    assert scores == sorted(scores, reverse=True)
    assert client.get("/api/products/999999999/similar").status_code == 404


def test_compare(client):
    ids = _some_ids(client, 3)
    r = client.post("/api/compare", json={"ids": ids})
    assert r.status_code == 200
    body = r.json()
    assert len(body["products"]) == 3
    assert body["cheapest_id"] == min(body["products"], key=lambda p: p["price"])["id"]
    assert client.post("/api/compare", json={"ids": [_some_ids(client, 1)[0]]}).status_code == 422
    assert client.post("/api/compare", json={"ids": [_some_ids(client, 1)[0], 999999999]}).status_code == 404
