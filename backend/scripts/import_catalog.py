"""Import the Kaggle-derived catalogue (data/catalog_source.csv + images) into StyleScout's format.

What it does
  1. Reads catalog_source.csv (columns: id, name, article_type, colour, gender, usage, price_inr,
     source_store, image_file ...).
  2. Maps the dataset's 47 article types and 39 colours onto a smaller, cleaner vocabulary
     (the same vocabulary CLIP's zero-shot attribute prompts use - see services/attributes.py).
  3. HOLDS OUT a few photos per category. They are NOT put in the searchable catalogue; they become
     sample query photos (data/sample_queries) and the test set for scripts/evaluate.py. This is
     how we can honestly measure search quality: the query item is never in the index.
  4. Writes data/products.json (+ copies images to data/images).

Run (from backend/):  python -m scripts.import_catalog --source <folder containing images/>
"""
import argparse
import csv
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HOLDOUT_PER_CATEGORY = 3

CATEGORY_MAP = {
    "Dresses": "dress", "Tshirts": "t-shirt", "Shirts": "shirt", "Tops": "top", "Tunics": "tunic",
    "Kurtas": "kurta", "Kurtis": "kurta", "Kurta Sets": "kurta",
    "Jeans": "jeans", "Trousers": "trousers", "Track Pants": "track pants", "Shorts": "shorts",
    "Capris": "capris", "Leggings": "leggings", "Jeggings": "leggings", "Tights": "leggings",
    "Skirts": "skirt", "Jackets": "jacket", "Rain Jacket": "jacket", "Sweaters": "sweater",
    "Sweatshirts": "sweatshirt", "Sarees": "saree", "Dupatta": "dupatta",
    "Patiala": "salwar", "Salwar": "salwar", "Churidar": "salwar", "Salwar and Dupatta": "salwar",
    "Flats": "flats", "Heels": "heels", "Sandals": "sandals", "Sports Sandals": "sandals",
    "Flip Flops": "flip flops", "Casual Shoes": "casual shoes", "Formal Shoes": "formal shoes",
    "Sports Shoes": "sports shoes",
}
COLOUR_MAP = {
    "Navy Blue": "navy", "Grey Melange": "grey", "Charcoal": "grey", "Off White": "white", "Cream": "cream",
    "Khaki": "beige", "Taupe": "beige", "Nude": "beige", "Turquoise Blue": "teal", "Sea Green": "teal",
    "Magenta": "pink", "Peach": "orange", "Rust": "brown", "Tan": "brown", "Coffee Brown": "brown",
    "Copper": "brown", "Bronze": "brown", "Lavender": "purple", "Mauve": "purple", "Metallic": "silver",
    "Mustard": "yellow", "Multi": "multicolour",
}


def clean_category(row):
    return CATEGORY_MAP.get(row["article_type"], row["article_type"].lower())


def clean_colour(row):
    return COLOUR_MAP.get(row["colour"], row["colour"].lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True, help="folder that contains the images/ directory")
    args = ap.parse_args()

    with open(DATA_DIR / "catalog_source.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    rng = random.Random(42)
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[clean_category(r)].append(r)

    holdout_ids = set()
    for cat, items in by_cat.items():
        if len(items) >= 20:  # do not hold out from tiny categories
            holdout_ids.update(r["id"] for r in rng.sample(items, HOLDOUT_PER_CATEGORY))

    images_out, holdout_out, samples_out = DATA_DIR / "images", DATA_DIR / "holdout_images", DATA_DIR / "sample_queries"
    for d in (images_out, holdout_out, samples_out):
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.jpg"):
            old.unlink()

    products, holdout = [], []
    for r in rows:
        src = args.source / r["image_file"]
        category, colour = clean_category(r), clean_colour(r)
        if r["id"] in holdout_ids:
            shutil.copy(src, holdout_out / f"{r['id']}.jpg")
            holdout.append({"id": int(r["id"]), "name": r["name"], "category": category, "color": colour})
            continue
        shutil.copy(src, images_out / f"{r['id']}.jpg")
        products.append({
            "id": int(r["id"]),
            "name": r["name"],
            "category": category,
            "image_url": f"/images/{r['id']}.jpg",
            "price": float(r["price_inr"]),
            "platform": r["source_store"].split("-")[0].strip(),
            "description": f"Sample listing: {r['name']} ({r['gender']}, {r['usage'].lower()}). "
                           f"Demo data - the price and store are placeholders, not a real offer.",
            "color": colour,
            "gender": r["gender"],
            "usage": r["usage"],
            "product_url": f"https://example.com/demo-product/{r['id']}",
            "is_demo": True,
            "embedding_index": -1,
        })

    (DATA_DIR / "products.json").write_text(json.dumps(products, indent=1), encoding="utf-8")
    (DATA_DIR / "holdout.json").write_text(json.dumps(holdout, indent=1), encoding="utf-8")

    # a handful of varied sample query photos for the demo (one per popular category)
    shown = set()
    for h in holdout:
        if h["category"] in {"dress", "t-shirt", "jeans", "kurta", "heels", "casual shoes", "saree", "skirt", "jacket", "sweatshirt"} \
                and h["category"] not in shown:
            shown.add(h["category"])
            shutil.copy(holdout_out / f"{h['id']}.jpg",
                        samples_out / f"query_{h['category'].replace(' ', '-')}_{h['color']}_{h['id']}.jpg")

    print(f"{len(products)} products imported, {len(holdout)} photos held out for testing, "
          f"{len(shown)} sample queries.")


if __name__ == "__main__":
    main()
