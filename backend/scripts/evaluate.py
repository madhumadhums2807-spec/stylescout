"""Measure search quality on the HELD-OUT photos (items that are not in the searchable catalogue),
and compare different colour re-ranking strengths.

For every held-out photo we run a real search and check:
  * category@1 / @5 : does a result with the same category appear first / in the top 5?
  * precision@10    : of the top 10 results, what fraction have the correct category?
  * colour@1        : is the top result's colour label the same as the true colour?
  * detected category: does the zero-shot / neighbour-vote category equal the truth?

The table at the end shows how the COLOUR WEIGHT changes those numbers (0 = colour re-ranking off).
Pick the weight with the best colour@1 that does not hurt category@1, then set it with
    set STYLESCOUT_COLOUR_WEIGHT=0.3       (Windows cmd)   or change COLOUR_WEIGHT in app/config.py

Run from backend/:   python -m scripts.evaluate
"""
import json

from fastapi.testclient import TestClient

from app import config
from app.main import app

WEIGHTS = [0.0, 0.01, 0.02, 0.03, 0.05, 0.07]
holdout = json.loads((config.DATA_DIR / "holdout.json").read_text())


def evaluate(client, weight):
    cat1 = cat5 = col1 = attr_cat = 0
    prec10 = 0.0
    misses = []
    for h in holdout:
        path = config.DATA_DIR / "holdout_images" / f"{h['id']}.jpg"
        body = client.post("/api/search", files={"file": (path.name, path.read_bytes(), "image/jpeg")},
                           data={"top_k": 200, "colour_weight": weight}).json()
        res = body["results"]
        cats = [r["category"] for r in res]
        cat1 += cats[0] == h["category"]
        cat5 += h["category"] in cats[:5]
        col1 += res[0]["color"] == h["color"]
        prec10 += sum(c == h["category"] for c in cats[:10]) / 10
        attr_cat += body["attributes"]["category"]["label"] == h["category"]
        if cats[0] != h["category"]:
            misses.append((h["category"], cats[0]))
    n = len(holdout)
    return {"weight": weight, "cat1": cat1 / n, "cat5": cat5 / n, "prec10": prec10 / n,
            "col1": col1 / n, "attr": attr_cat / n, "misses": misses}


with TestClient(app) as client:
    embedder = client.get("/api/health").json()["embedder"]
    print(f"Embedder: {embedder} | held-out photos: {len(holdout)} | default colour weight: {config.COLOUR_WEIGHT}")
    print(f"{'weight':>7} {'category@1':>11} {'category@5':>11} {'precision@10':>13} {'colour@1':>9}")
    rows = []
    for w in WEIGHTS:
        r = evaluate(client, w)
        rows.append(r)
        print(f"{w:>7} {r['cat1']:>11.0%} {r['cat5']:>11.0%} {r['prec10']:>13.0%} {r['col1']:>9.0%}")
    print(f"\nDetected category correct (zero-shot, independent of weight): {rows[0]['attr']:.0%}")
    print("Top-1 category confusions at weight 0 (true -> returned):", rows[0]["misses"][:12])
