"""Pydantic models = the shape of every JSON response. FastAPI validates and documents them."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    image_url: str
    price: float
    platform: str
    description: str = ""
    color: str = ""
    gender: str = ""
    usage: str = ""
    product_url: str = ""
    is_demo: bool = True


class ScoredProduct(ProductOut):
    score: float = Field(description="Cosine similarity, -1..1 (higher = more similar)")
    match_percent: int = Field(description="score shown as 0-100 for the UI")


class Attribute(BaseModel):
    label: str
    confidence: float


class DetectedAttributes(BaseModel):
    method: str  # "clip-zero-shot" or "neighbour-vote"
    category: Optional[Attribute] = None
    colour: Optional[Attribute] = None


class DominantColour(BaseModel):
    name: str
    hex: str


class SearchResponse(BaseModel):
    results: List[ScoredProduct]
    attributes: DetectedAttributes
    dominant_colour: DominantColour
    embedder: str
    colour_weight: float = 0.0
    looks_like_fashion: Optional[bool] = None  # None = could not check (fallback embedder)
    fashion_confidence: Optional[float] = None
    total_retrieved: int
    total_after_filters: int
    filters_applied: dict
    elapsed_ms: int


class CompareRequest(BaseModel):
    ids: List[int] = Field(min_length=2, max_length=4)


class CompareResponse(BaseModel):
    products: List[ProductOut]
    cheapest_id: int


class HealthResponse(BaseModel):
    status: str
    embedder: str
    products: int
    index_vectors: int
