"""Pure-Python filtering and sorting of already-retrieved results (no AI involved)."""
from typing import Iterable, List, Optional

SORT_OPTIONS = {"match", "price_asc", "price_desc"}


def apply_filters(items: Iterable[dict], min_price: Optional[float] = None,
                  max_price: Optional[float] = None, platforms: Optional[List[str]] = None) -> List[dict]:
    wanted = {p.lower() for p in platforms} if platforms else None
    out = []
    for item in items:
        if min_price is not None and item["price"] < min_price:
            continue
        if max_price is not None and item["price"] > max_price:
            continue
        if wanted and item["platform"].lower() not in wanted:
            continue
        out.append(item)
    return out


def sort_items(items: List[dict], sort: str = "match") -> List[dict]:
    if sort == "price_asc":
        return sorted(items, key=lambda x: x["price"])
    if sort == "price_desc":
        return sorted(items, key=lambda x: x["price"], reverse=True)
    return sorted(items, key=lambda x: x.get("score", 0), reverse=True)  # "match" (default)
