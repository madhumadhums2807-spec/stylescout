"""POST /api/search - the core feature: image in, similar products out."""
import time
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import config
from ..database import get_db
from ..models import Product
from ..schemas import DominantColour, ProductOut, SearchResponse
from ..services import attributes, colour_rerank, filtering, image_processing
from ..services.embedding import get_embedder
from ..services.vector_store import store
from ..utils.validators import read_and_validate_image

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(
    file: UploadFile = File(...),
    min_price: Optional[float] = Form(None),
    max_price: Optional[float] = Form(None),
    platforms: Optional[str] = Form(None, description="comma-separated, e.g. 'Amazon,Myntra'"),
    sort: str = Form("match"),
    top_k: int = Form(config.DEFAULT_TOP_K),
    colour_weight: Optional[float] = Form(None, description="0 = off; default from config"),
    db: Session = Depends(get_db),
):
    started = time.perf_counter()

    # 1) validate -> 2) preprocess
    if sort not in filtering.SORT_OPTIONS:
        raise HTTPException(422, f"sort must be one of {sorted(filtering.SORT_OPTIONS)}")
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(422, "min_price cannot be greater than max_price")
    if colour_weight is not None and not 0 <= colour_weight <= 2:
        raise HTTPException(422, "colour_weight must be between 0 and 2")
    weight = config.COLOUR_WEIGHT if colour_weight is None else colour_weight
    data = await read_and_validate_image(file)
    image = image_processing.preprocess(data)
    colour_name, colour_hex = image_processing.dominant_colour(image)

    # 3) embed the query image
    embedder = get_embedder()
    query_vec = embedder.embed_images([image])[0]

    # 3b) colour re-ranking signal: CLIP's probability that the photo is each colour
    #     (only possible with a text-capable embedder, i.e. real CLIP)
    colour_sims = None
    if weight > 0 and embedder.supports_text:
        colour_sims = colour_rerank.similarities(attributes.colour_probabilities(query_vec, embedder))
    applied_weight = weight if colour_sims is not None else 0.0

    # 4) nearest neighbours from FAISS
    k = max(1, min(top_k, config.MAX_TOP_K))
    row_ids, scores = store.search(query_vec, k)
    score_by_row = dict(zip(row_ids, scores))
    products = db.query(Product).filter(Product.embedding_index.in_(row_ids)).all()

    items = []
    for p in products:
        s = float(score_by_row[p.embedding_index])
        out = ProductOut.model_validate(p, from_attributes=True).model_dump()
        if colour_sims is not None:  # blend visual similarity with colour similarity
            s = (s + weight * float(colour_sims[p.embedding_index])) / (1 + weight)
        out["score"] = round(s, 4)
        out["match_percent"] = max(0, min(100, round(s * 100)))
        items.append(out)
    items = filtering.sort_items(items, "match")

    # 5) detect attributes (zero-shot with CLIP, otherwise neighbour vote)
    looks_like_fashion = fashion_confidence = None
    if embedder.supports_text:
        detected = attributes.detect_with_clip(query_vec, embedder)
        looks_like_fashion, fashion_confidence = attributes.fashion_check(query_vec, embedder)
    else:
        detected = attributes.detect_by_neighbours(items[: config.NEIGHBOURS_FOR_ATTRIBUTES])

    # 6) filters + sort
    platform_list = [p.strip() for p in platforms.split(",") if p.strip()] if platforms else None
    filtered = filtering.apply_filters(items, min_price, max_price, platform_list)
    filtered = filtering.sort_items(filtered, sort)

    return SearchResponse(
        results=filtered,
        attributes=detected,
        dominant_colour=DominantColour(name=colour_name, hex=colour_hex),
        embedder=embedder.name,
        colour_weight=applied_weight,
        looks_like_fashion=looks_like_fashion,
        fashion_confidence=fashion_confidence,
        total_retrieved=len(items),
        total_after_filters=len(filtered),
        filters_applied={"min_price": min_price, "max_price": max_price, "platforms": platform_list, "sort": sort},
        elapsed_ms=round((time.perf_counter() - started) * 1000),
    )
