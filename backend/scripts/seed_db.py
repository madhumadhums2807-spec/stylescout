"""Create tables and load data/products.json into SQLite (safe to re-run).
Run from backend/:  python -m scripts.seed_db"""
from app.database import Base, SessionLocal, engine
from app.main import seed_if_empty

Base.metadata.create_all(bind=engine)
db = SessionLocal()
seed_if_empty(db)
db.close()
print("Database ready.")
