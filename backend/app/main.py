"""FastAPI entry point. Run with:  uvicorn app.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config
from .database import Base, SessionLocal, engine
from .models import Product
from .routers import compare, products, search
from .services.embedding import get_embedder
from .services import colour_rerank
from .services.providers import DemoProvider
from .services.vector_store import ensure_index

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("stylescout")


def seed_if_empty(db) -> None:
    """First run: load the demo products from products.json into SQLite."""
    if db.query(Product).count() > 0:
        return
    rows = DemoProvider(config.PRODUCTS_JSON).fetch_products()
    db.add_all([Product(**row) for row in rows])
    db.commit()
    log.info("Seeded %d demo products.", len(rows))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at startup: tables -> seed -> load the model ONCE -> load/build the FAISS index
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
        embedder = get_embedder()
        ensure_index(db, embedder)
        colour_rerank.ensure_features(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="StyleScout API",
    description="Search fashion by image. Product data is demo data (is_demo=true).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/images", StaticFiles(directory=config.IMAGES_DIR), name="images")

app.include_router(search.router)
app.include_router(products.router)
app.include_router(compare.router)
