"""TF-IDF + cosine-similarity menu item recommender (scikit-learn, no LLM)."""
from __future__ import annotations

import logging

from backend.data import store
from backend.models.menu import MenuItem

logger = logging.getLogger(__name__)

# Module-level state, mutated only via the _STATE dict
_STATE: dict = {"index": None, "items": None}


def _build_index() -> None:
    """Build the TF-IDF matrix and cosine similarity matrix once."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    items = store.get_menu_items(None)
    if not items:
        _STATE["index"] = {}
        _STATE["items"] = []
        return

    docs = [f"{i.name} {i.category} {i.description}" for i in items]
    ids = [i.id for i in items]

    tfidf = TfidfVectorizer(stop_words="english")
    matrix = tfidf.fit_transform(docs)
    sim = cosine_similarity(matrix)

    _STATE["items"] = items
    _STATE["index"] = {"ids": ids, "sim": sim}
    logger.info("Recommender index built for %d items", len(items))


def _ensure_index() -> None:
    if _STATE["index"] is None:
        _build_index()


def recommend(item_id: int, limit: int = 3) -> list[MenuItem]:
    """Return up to *limit* items most similar to *item_id* (excluding itself)."""
    _ensure_index()
    idx_data = _STATE["index"]
    items = _STATE["items"]
    if not idx_data or not items:
        return []

    ids = idx_data["ids"]
    sim = idx_data["sim"]

    if item_id not in ids:
        return []

    idx = ids.index(item_id)
    scores = list(enumerate(sim[idx]))
    scores = [(i, s) for i, s in scores if i != idx]
    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:limit]
    return [items[i] for i, _ in top]


def recommend_cart(item_ids: list[int], limit: int = 3) -> list[MenuItem]:
    """Return items most similar to the average profile of *item_ids*."""
    _ensure_index()
    idx_data = _STATE["index"]
    items = _STATE["items"]
    if not idx_data or not items:
        return []

    import numpy as np

    ids = idx_data["ids"]
    sim = idx_data["sim"]

    valid_indices = [ids.index(i) for i in item_ids if i in ids]
    if not valid_indices:
        return []

    avg = sim[valid_indices].mean(axis=0)
    for vi in valid_indices:
        avg[vi] = -1  # exclude items already in cart
    ranked = np.argsort(avg)[::-1]
    return [items[i] for i in ranked[:limit]]


def reset_index() -> None:
    """Clear the cached index (used by tests)."""
    _STATE["index"] = None
    _STATE["items"] = None
