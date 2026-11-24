"""Product providers.

Today every product comes from the demo database (see `DemoProvider`). To integrate a real
store later, implement `ProductProvider` for it (using that store's *authorised* API) and
register it - the search, filtering and UI code do not change.
"""
from abc import ABC, abstractmethod
from typing import List


class ProductProvider(ABC):
    name: str

    @abstractmethod
    def fetch_products(self) -> List[dict]:
        """Return products as dicts with the same keys as the `products` table."""


class DemoProvider(ProductProvider):
    name = "demo"

    def __init__(self, products_json_path):
        self.path = products_json_path

    def fetch_products(self) -> List[dict]:
        import json

        with open(self.path, encoding="utf-8") as f:
            return json.load(f)
