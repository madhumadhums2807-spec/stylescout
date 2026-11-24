"""Catalogue endpoints: list/filter products, one product, platform names, health."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Product
from ..schemas import HealthResponse, ProductOut, ScoredProduct
from ..services.embedding import get_embedder
from ..services.vector_store import store

router = APIRouter(prefix="/api", tags=["products"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    return HealthResponse(
        status="ok",
        embedder=get_embedder().name,
        products=db.query(func.count(Product.id)).scalar(),
        index_vectors=store.size,
    )


@router.get("/products", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = None,
    platform: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    q: Optional[str] = Query(None, description="text search in the product name"),
    sort: str = Query("price_asc", pattern="^(price_asc|price_desc|name)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())
    if platform:
        query = query.filter(func.lower(Product.platform) == platform.lower())
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    order = {"price_asc": Product.price.asc(), "price_desc": Product.price.desc(), "name": Product.name.asc()}[sort]
    return query.order_by(order).offset(offset).limit(limit).all()


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product


@router.get("/products/{product_id}/similar", response_model=List[ScoredProduct])
def similar_products(
    product_id: int,
    limit: int = Query(12, ge=1, le=48),
    same_category: bool = Query(True, description="only return products of the same category"),
    db: Session = Depends(get_db),
):
    """'More like this': the nearest catalogue products to ONE product, using that product's own vector."""
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    row = product.embedding_index
    if row is None or row < 0 or row >= store.size:
        raise HTTPException(503, "Search index is not ready for this product")

    query_vec = store.index.reconstruct(int(row))  # the product's stored vector
    pool = min(store.size, max(limit * 8, 80)) if same_category else min(store.size, limit + 1)
    rows, scores = store.search(query_vec, pool)
    score_by_row = dict(zip(rows, scores))

    candidates = db.query(Product).filter(Product.embedding_index.in_(rows), Product.id != product.id).all()
    if same_category:
        candidates = [p for p in candidates if p.category == product.category]
    candidates.sort(key=lambda p: score_by_row[p.embedding_index], reverse=True)

    out = []
    for p in candidates[:limit]:
        s = float(score_by_row[p.embedding_index])
        item = ProductOut.model_validate(p, from_attributes=True).model_dump()
        out.append(ScoredProduct(**item, score=round(s, 4), match_percent=max(0, min(100, round(s * 100)))))
    return out


@router.get("/platforms", response_model=List[str])
def platforms(db: Session = Depends(get_db)):
    rows = db.query(Product.platform).distinct().order_by(Product.platform).all()
    return [r[0] for r in rows]


@router.get("/categories", response_model=List[str])
def categories(db: Session = Depends(get_db)):
    rows = db.query(Product.category).distinct().order_by(Product.category).all()
    return [r[0] for r in rows]
