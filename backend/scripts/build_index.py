"""Embed every product image and (re)build the FAISS index.
Run from backend/:  python -m scripts.build_index"""
from app import config
from app.database import Base, SessionLocal, engine
from app.main import seed_if_empty
from app.services.embedding import get_embedder
from app.services.vector_store import ensure_index

for f in (config.FAISS_PATH, config.FAISS_META_PATH):
    f.unlink(missing_ok=True)
Base.metadata.create_all(bind=engine)
db = SessionLocal()
seed_if_empty(db)
embedder = get_embedder()
ensure_index(db, embedder)
db.close()
print(f"Index built with {embedder.name}.")
