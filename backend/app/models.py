"""Database tables. Embeddings are NOT stored here - they live in the FAISS index.
`embedding_index` is the row number of the product's vector inside that index."""
from sqlalchemy import Boolean, Column, Float, Integer, String, Text

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), index=True, nullable=False)
    image_url = Column(String(300), nullable=False)
    price = Column(Float, nullable=False)
    platform = Column(String(50), index=True, nullable=False)
    description = Column(Text, default="")
    color = Column(String(30), default="")
    gender = Column(String(20), default="")
    usage = Column(String(30), default="")
    product_url = Column(String(300), default="")
    is_demo = Column(Boolean, default=True, nullable=False)
    embedding_index = Column(Integer, default=-1)
