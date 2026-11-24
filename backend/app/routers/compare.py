"""POST /api/compare - return 2-4 chosen products side by side."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Product
from ..schemas import CompareRequest, CompareResponse

router = APIRouter(prefix="/api", tags=["compare"])


@router.post("/compare", response_model=CompareResponse)
def compare(body: CompareRequest, db: Session = Depends(get_db)):
    ids = list(dict.fromkeys(body.ids))  # drop duplicates, keep order
    products = db.query(Product).filter(Product.id.in_(ids)).all()
    if len(products) != len(ids):
        raise HTTPException(404, "One or more products were not found")
    by_id = {p.id: p for p in products}
    ordered = [by_id[i] for i in ids]
    cheapest = min(ordered, key=lambda p: p.price)
    return CompareResponse(products=ordered, cheapest_id=cheapest.id)
