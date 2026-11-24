# StyleScout - Viva Preparation Guide

Read this in order. Part 1-3 = understand the system. Part 4 = file-by-file tour. Part 5 = questions with model answers. Part 6 = demo script. Part 7 = honest limitations (examiners respect honesty far more than bluffing).

---

## 1. The project in 30 seconds (memorise this)

> "Describing fashion in words is hard, so StyleScout lets you search with a photo. The backend converts the photo into a 512-number vector using the CLIP model, finds the closest product vectors with FAISS, and returns them with a match percentage. The React frontend lets the user filter by budget and platform and compare products. All product data is clearly labelled demo data."

## 2. How one search works (draw this on the board)

```
Browser: upload photo ──POST /api/search──►  FastAPI
   1. validators.py     : extension, MIME type, size <= 5 MB, Pillow can really open it
   2. image_processing  : fix rotation, flatten transparency, convert to RGB, resize to <=512px,
                          k-means to find the dominant colour
   3. embedding.py      : CLIP image encoder -> 512 numbers -> L2-normalise (length = 1)
   4. vector_store.py   : FAISS IndexFlatIP -> top-K closest product vectors + scores
   5. SQLite            : fetch product details for those row numbers
   6. attributes.py     : CLIP zero-shot -> "dress / red / floral" (+ confidence)
   7. filtering.py      : price range, platforms, sort (only if the request asked for it)
   ◄── JSON ──  results + attributes + dominant colour
Browser: shows cards; moving a slider re-filters locally (no AI re-run, so it is instant)
```

## 3. The four ideas you must understand

**Embedding** - a list of 512 numbers describing what an image "means". Similar-looking items get nearby lists. Keyword search can't do this because there are no keywords in a photo.

**CLIP** - a model trained on ~400 million (image, caption) pairs so that a photo and its caption land near each other. Two consequences: (1) image-to-image similarity works with no training from us; (2) we can compare an image with *text* like "a photo of a red dress" - that is **zero-shot** classification (no labelled training data of our own).

**Cosine similarity / normalisation** - similarity = the angle between two vectors. If every vector is scaled to length 1, cosine similarity equals the plain dot product (inner product). FAISS `IndexFlatIP` computes dot products very fast, so normalising first gives us cosine similarity "for free". Score 1.0 = identical direction.

**FAISS** - Meta's library for nearest-neighbour search over vectors. `IndexFlat` is exact brute force: compare the query with all 2,913 vectors. That is perfectly fine at this size. For millions of products you'd switch to approximate indexes (IVF or HNSW), trading a little accuracy for big speed.

## 4. File-by-file tour

### Backend (`backend/app/`)
| File | What it does | Say this if asked |
|---|---|---|
| `main.py` | Creates the FastAPI app. The `lifespan` function runs once at startup: create tables -> seed products -> load the model **once** -> load or build the FAISS index. Also mounts `/images` and CORS. | "Loading CLIP takes seconds, so we do it at startup, not per request." |
| `config.py` | All settings (paths, model name, upload limits, top-K). Env variables override. | "No magic numbers scattered in code." |
| `database.py`, `models.py` | SQLAlchemy engine/session and the `Product` table. | "Change one URL string to move to PostgreSQL." |
| `schemas.py` | Pydantic models for responses. | "Gives automatic validation and the `/docs` page." |
| `utils/validators.py` | Upload checks. | "We never trust the filename; we actually try to decode the bytes." |
| `services/image_processing.py` | Pillow/OpenCV: EXIF rotation, RGBA->RGB on white, resize, HSV colour naming, k-means dominant colour ignoring the background. | "Uses OpenCV `kmeans` on a 64x64 copy; background = median colour of the border." |
| `services/embedding.py` | `ClipEmbedder` (real) and `FallbackEmbedder` (handmade colour/edge/shape features, for offline testing). `get_embedder()` picks one. | "Fallback exists only so the app runs without a 600 MB download." |
| `services/attributes.py` | Zero-shot category and colour (26 categories, 19 colours) using text prompts + softmax; also `fashion_check`, which decides whether the upload is clothing at all. | "softmax of 100 x cosine similarity; 100 is CLIP's learned temperature." |
| `services/vector_store.py` | Build/save/load/search FAISS. Stores which embedder built the index and rebuilds if it changes. | "Vectors from different models are not comparable, so we guard against mixing." |
| `services/colour_rerank.py` | Colour re-ranking: blends CLIP's colour probabilities for the query photo with each product's labelled colour. | "CLIP is weak at exact colour, so we add a colour bonus; the weight is tunable and we measured it." |
| `services/filtering.py` | Pure Python filters and sorting. | "No AI here - plain logic." |
| `services/providers/` | `ProductProvider` interface + `DemoProvider`. | "Future Amazon/Myntra integration plugs in here via their authorised APIs." |
| `routers/search.py` | `POST /api/search`. | The core endpoint, follows the 7 steps in Part 2. |
| `routers/products.py` | health, list products (with filters), detail, platforms, categories. | |
| `routers/compare.py` | `POST /api/compare` takes 2-4 ids, returns them and the cheapest. | |
| `scripts/import_catalog.py` | Cleans the Kaggle catalogue (47 article types -> 26 main categories, 39 colours -> ~20), holds out test photos, writes `products.json`. | "We held out 87 photos so the query item is never in the index." |
| `scripts/evaluate.py` | Runs every held-out photo through the real search and reports category@1/@5, precision@10, colour@1. | "Our evaluation: measured, not guessed." |
| `scripts/check_clip.py` | First-run check that real CLIP loads and works. | |

### Why embeddings live in FAISS and details in SQLite
Vectors are fixed-size numeric arrays that need fast similarity maths; product info is structured data that needs queries (`WHERE price < 1000`). Each tool does what it is good at. They are linked by `products.embedding_index` = row number in the FAISS index.

### Frontend (`frontend/src/`)
| File | Role |
|---|---|
| `App.jsx` | Holds the main state (file, results, filters, compare list) and decides which page to show. |
| `pages/Home.jsx`, `pages/Results.jsx` | Upload page and results page. `Results` does the **local filtering** with `useMemo`. |
| `components/UploadZone.jsx` | Drag-and-drop, preview, client-side type/size check. |
| `components/FilterPanel.jsx` | Price sliders, platform chips, sort. Controlled component: parent owns the state. |
| `components/ProductCard.jsx`, `DemoBadge.jsx` | Card with match %, demo badge, compare button. |
| `components/CompareDrawer.jsx` | Side-by-side table, fetched from `/api/compare`. |
| `components/DetectedAttributes.jsx` | Shows detected category and colour, worded as guesses. |
| `services/api.js` | All `fetch` calls in one place, with error parsing. |
| `vite.config.js` | Dev proxy: `/api` and `/images` forward to port 8000, avoiding CORS issues. |

## 5. Questions you will probably be asked

**Concept**
1. *Why embeddings instead of keyword search?* Photos have no keywords; embeddings capture visual meaning, so "looks similar" becomes "is numerically close".
2. *What does CLIP do that a normal CNN classifier doesn't?* A CNN classifier is trained for a fixed label set and can only output those labels. CLIP learned a shared image-text space, so it can compare images to any text description and to other images without retraining.
3. *What is zero-shot?* Classifying into categories the model was never explicitly trained on, by comparing the image to text prompts like "a photo of a striped shirt".
4. *Why normalise vectors?* So inner product = cosine similarity; then the score depends only on direction, not vector length, and FAISS can use the fast inner-product index.
5. *Cosine similarity vs Euclidean distance?* For normalised vectors they rank results identically; cosine is the standard choice for embeddings.
6. *What is the dimension of the vectors?* 512 for CLIP ViT-B/32. "ViT-B/32" = Vision Transformer, Base size, 32x32 pixel patches.
7. *What does "match %" mean?* The cosine similarity x 100. It's a relative ranking signal, not a probability of being the same product.
8. *Why FAISS and not a SQL query?* SQL can't rank by vector similarity efficiently; FAISS is built for it.
9. *Does FAISS scale?* Flat search is exact but linear. At 1M+ items use IVF/HNSW or a managed vector DB.

**Design choices**
10. *Why FastAPI?* Async support, auto-generated `/docs`, Pydantic validation, and Python is where the ML libraries are.
11. *Why SQLite?* Zero setup for a demo; SQLAlchemy means switching to PostgreSQL is a config change.
12. *Why load the model at startup?* Loading takes seconds and memory; per-request loading would make every search slow.
13. *Why filter in the browser?* The 100 retrieved results are already in memory; re-filtering is instant and avoids re-running the AI. The backend also supports server-side filters (`min_price`, `max_price`, `platforms`, `sort`) - tested in `test_api.py` - which is what you'd use for large result sets or a paginated API.
14. *Why a `providers/` folder?* Separation of "where products come from" from "how search works". Real marketplaces need authorised APIs, partner agreements and terms compliance; we did not scrape them.
15. *Why React + Vite + Tailwind?* Component model, fast dev server, utility CSS for responsive layout.

**Security / robustness**
16. *How do you validate uploads?* Extension, MIME type, size limit (read one byte past the limit), and Pillow must actually decode the bytes; minimum dimensions. Done server-side because client checks can be bypassed.
17. *What happens with a transparent PNG?* We composite it onto white; otherwise transparent pixels become black and distort colours and embeddings.
18. *What about phone photos that appear rotated?* `ImageOps.exif_transpose` applies the EXIF orientation.
19. *Do you store users' images?* No, uploads are processed in memory and not saved.

**Honesty / limitations**
20. *Is this live product data?* No. The 2,913 product photos and names come from a public Kaggle fashion dataset, but the prices, store names (Myntra/Ajio/Meesho) and links are placeholders supplied for the demo (`is_demo = true`), and the UI says so on the banner, each card and the footer.
21. *How accurate is it?* Zero-shot attributes can be wrong, so the UI shows them as "detected" with a confidence. Categories like t-shirt/shirt or sweater/sweatshirt are genuinely close, so most mistakes are between neighbouring categories (see the confusion list printed by `scripts.evaluate`).
22. *How did you evaluate?* 8 automated API tests, plus `scripts/evaluate.py`: 87 photos were held out of the catalogue (3 per category), each is searched as if a user uploaded it, and we measure whether the top result has the right category (category@1), whether the right category is in the top 5, precision@10, and colour@1. Our measured results with real CLIP are in Part 5b.
23. *What would you improve?* Real catalogue via authorised APIs, approximate index, fine-tuning CLIP on fashion data, user accounts and saved searches, caching, Docker deployment.
24. *What would break at scale?* Flat FAISS search, SQLite concurrency, in-process model (move to a separate inference service/GPU).
25. *What if someone uploads a photo that is not clothing?* We run a zero-shot check with CLIP: the image is compared with clothing prompts ("a photo of clothing", "shoes", "a person wearing an outfit"...) and non-clothing prompts ("landscape", "animal", "food", "building"...). If the probability of "clothing" is below 50%, the UI shows a warning instead of meaningless matches (with a button to see the closest products anyway). We tested a wallpaper (blocked) and a portrait of a person in an outfit (allowed).
28. *How does a user actually buy the item?* Each result card has a "Shop on <store>" button, plus quick links to Amazon, Flipkart and Meesho. They open that store's own search page for the product name. We cannot link to a live product page because our catalogue is demo data and has no real product URLs; a direct link needs the store's authorised product or affiliate API (for example Amazon's Product Advertising API or the Flipkart affiliate API), which needs an approved account. That is our stated future work. The sample price shown is a placeholder, and the card says so.
29. *Why not scrape the shopping sites for real prices and links?* Most marketplaces' terms forbid scraping, pages change often and block bots, and showing scraped prices as if they were live is misleading. Using authorised APIs is the correct route.
30. *What happens when the user picks a store?* An in-app "store view" opens. The dress they chose is shown first (large photo, price, tags, a "Continue to <store>" button), and below it the app lists more products like it. The "similar" list comes from `GET /api/products/{id}/similar`.
31. *How does "similar to this dress" work without a new upload?* Every product's CLIP vector is already stored in FAISS. We fetch that vector with `index.reconstruct(row)`, search FAISS with it, drop the product itself, keep the same category and return the top 12. It is the same cosine-similarity search as the photo search, with a stored vector as the query.
32. *Why can't you show the real Meesho/Flipkart/Amazon page inside the app?* Those sites block embedding in other pages, and our catalogue is demo data with no real product IDs. So the store view is our own page, and the button opens that store's search for the item in a new tab. With an authorised affiliate or product API, the button could open the exact product page.
33. *How does the wishlist work, and where is the data stored?* The heart button calls a small React hook (`hooks/useWishlist.js`) that keeps the saved products in state and copies them to the browser's `localStorage`. So saved items survive a page reload, but only on that browser and device; there are no user accounts and nothing is sent to the server. The whole product object is saved, so the Saved page works without searching again.
34. *Why is filtering and sorting done in the browser, not the API?* The search returns the top 200 matches once. The budget, store, category, colour, gender and occasion filters and the sort are then plain JavaScript over that list (`services/facets.js`, with `useMemo`). Changing a filter is instant and never re-runs the AI model.
35. *Where do the filter options come from?* From the results themselves: we count how many results have each category, colour, gender and occasion, and show those counts on the chips (for example "Shirt 49"). Options with no results are not shown, and meaningless labels such as "NA" are hidden. Within one group, choices are OR (Red or Blue); across groups they are AND (Women and Red and Casual).
26. *Why was colour matching weak, and what did you do about it?* CLIP embeddings capture shape and overall style more strongly than exact colour (colour@1 was 37%). We tried two fixes. First, picking the photo's dominant colour from pixels (k-means): we measured it on the held-out photos and it was right for under half of them, because many catalogue photos show a person (skin, hair) and the images are tiny, so we dropped it. Second, colour re-ranking with CLIP itself: CLIP gives a probability for each of 19 colour names for the uploaded photo, and each product gets a bonus equal to the probability of its (reliable, labelled) colour: `final = (clip_similarity + W x colour_match) / (1 + W)`. The weight W is configurable (`COLOUR_WEIGHT`), and `scripts/evaluate.py` sweeps W and shows the effect on category@1 and colour@1 so the value is chosen from data, not guessed.
27. *What is the trade-off in colour re-ranking?* A larger W favours colour over shape, so colour@1 can rise while category@1 falls (e.g. a red skirt outranking a blue skirt-shaped item less often, but a red top could outrank a better-shaped skirt). Choosing W is choosing that balance. In our sweep, weights of 0.1 and above lost about 9 points of category@1, while 0.03 kept category@1 at 70% (from 71%) and raised colour@1 from 37% to 56%.

## 5b. Your measured results (say these numbers, they are yours)
Measured on 22 Nov 2026 with real CLIP (ViT-B/32) on 87 held-out photos across 26 categories (`python -m scripts.evaluate`):

| Measure | Result | Meaning |
|---|---|---|
| category@1 | **71%** | the first result has the right category |
| category@5 | **90%** | the right category appears in the top 5 |
| precision@10 | **63%** | on average 6 of the top 10 results have the right category |
| colour@1 | **37%** | the first result has exactly the same colour label |
| detected category correct | **56%** | the zero-shot "What we detected" label is right |

How to talk about them: random guessing over 26 categories would give about 4%, so 71% is far above chance. Mistakes are mostly between neighbouring categories (leggings/capris, capris/shorts, flip flops/sandals, sweater/top), which people also confuse. Colour is the weakest result (see limitations). The simple colour-and-shape stand-in used while developing scored 53% category@1, so CLIP clearly adds value. The test set is small (87 photos), so treat the percentages as indicative, not exact.

## 5c. Colour re-ranking results (your measured sweep, 87 held-out photos, real CLIP)

| colour weight | category@1 | category@5 | precision@10 | colour@1 |
|---|---|---|---|---|
| 0.0 (off) | 71% | 90% | 63% | 37% |
| 0.01 | 74% | 89% | 61% | 45% |
| 0.02 | 71% | 90% | 59% | 51% |
| **0.03 (chosen)** | **70%** | 87% | 58% | **56%** |
| 0.05 | 70% | 85% | 54% | 61% |
| 0.07 | 64% | 86% | 52% | 56% |
| 0.1 | 63% | 86% | 50% | 56% |
| 0.2 | 62% | 85% | 48% | 57% |
| 0.3 and above | 61% | 85% | 46% | 56% |

How to explain it:
- **Problem:** CLIP matched shape and style well but exact colour poorly (colour@1 = 37%).
- **Attempt 1 (dropped):** dominant colour from pixels; right for under half of photos (people's skin/hair, tiny images), so it added noise.
- **Attempt 2 (kept):** blend CLIP's colour probabilities for the query with each product's labelled colour.
- **Tuning:** a first sweep (0.1 to 0.8) showed all weights from 0.1 up were too strong (category@1 fell from 71% to about 62%). A finer sweep (0.01 to 0.07) found 0.03: colour@1 rose from 37% to 56% while category@1 stayed at 70%.
- **Why 0.03 and not 0.05:** 0.05 gives 61% colour but lower precision@10 (54% vs 58%); the colour gain over 0.03 is about 4 photos out of 87.
- **Caution:** with only 87 test photos, differences of 1-3 points are within noise.

## 6. Demo script (3-4 minutes)
1. Open the app; point at the **Demo data banner** ("we are explicit that this is sample data").
2. Upload a photo from `backend/data/sample_queries/` (e.g. the dress or kurta) -> show **What we detected** chips and the match percentages.
3. Drag the budget slider and click a platform chip -> "instant, no AI re-run".
4. Sort by price; add two products to **Compare** -> open the drawer, point out the lowest price highlight.
5. Upload a `.gif` or a text file renamed `.png` -> show the validation message. Then upload a non-clothing photo (a landscape) -> show the "doesn't look like a clothing photo" notice.
6. Open `http://127.0.0.1:8000/docs` -> show the auto-generated API docs and run `/api/health`.
7. Open `backend/app/routers/search.py` and walk through the 7 steps.

## 7. Honest limitations (say these before they ask)
- **Prices, store names and links are placeholders.** The catalogue has real product photos and names, but no real offers. Everything is labelled demo in the UI. A real version needs authorised store APIs or affiliate feeds (that is what `services/providers/` is for).
- **Images are small** (60x80 pixels), so cards look soft. CLIP shrinks images to 224x224 anyway, but higher-resolution photos would improve both look and accuracy.
- **Catalogue bias:** mostly Indian ethnic and casual wear, front-facing studio photos on plain backgrounds. A photo taken in a messy room or on a person walking may match worse. Zero-shot attributes can be wrong; the UI says "detected" and shows confidence.
- **Category granularity:** similar categories (t-shirt vs shirt, flats vs sandals) get confused. This is an inherent limit of visual similarity, not a bug.
- **Colour matching was weak (37% colour@1 before re-ranking).** CLIP focuses on shape and overall look more than exact colour. We added colour re-ranking (Part 5c); results depend on how well CLIP judges the colour of the uploaded photo, and the dataset's colour labels are subjective (navy vs blue vs black).
- **Busy photos match less well.** The catalogue is clean full-length studio photos, so a close-up portrait with a blurry background gets lower match scores (around 60% instead of 95%).
- **Tests vs real model:** the automated tests run with the lightweight fallback embedder (so they need no model download); the accuracy numbers in Part 5b and the UI use real CLIP.
- Stage 1 planned a `GET /api/products/filter` endpoint; the final design puts those filters on `GET /api/products` and on the search endpoint. Pattern detection (striped/floral) from Stage 1 was dropped because the catalogue has no pattern labels to check it against.

## 8. If you used an AI tool to help build it
Examiners may ask. Say plainly which parts were AI-assisted, and make sure *you* can explain every file in Part 4 and the flow in Part 2. Practise by changing something small live (for example the `DEFAULT_TOP_K` in `config.py`, or the colour list in `attributes.py`) and re-running the tests.
