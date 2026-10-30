"""Static gallery data mirrored from gallery.html.

Each dict maps directly to a ``GalleryItem`` Pydantic model.
The ``image`` paths are relative to the frontend root (i.e. the ``cafe/``
directory that FastAPI serves as StaticFiles).
"""
from __future__ import annotations

GALLERY_ITEMS: list[dict] = [
    {"id": 1,  "category": "Café",   "image": "Gallery/interior.jpg",         "label": "Warm café interior"},
    {"id": 2,  "category": "Coffee", "image": "Gallery/latte-art.jpg",         "label": "Latte art close-up"},
    {"id": 3,  "category": "Food",   "image": "Gallery/egg.jpg",               "label": "Fried egg toast"},
    {"id": 4,  "category": "Team",   "image": "Gallery/barista.jpg",           "label": "Barista pouring milk"},
    {"id": 5,  "category": "Café",   "image": "Gallery/cafe-lang.jpg",         "label": "Café signage & plants"},
    {"id": 6,  "category": "Café",   "image": "Gallery/lounge.jpg",            "label": "Cozy lounge corner"},
    {"id": 7,  "category": "Team",   "image": "Gallery/team.jpg",              "label": "Team behind the counter"},
    {"id": 8,  "category": "Food",   "image": "Gallery/croissant.jpg",         "label": "Fresh croissants"},
    {"id": 9,  "category": "Coffee", "image": "Gallery/ice.jpg",               "label": "Iced coffee with cream"},
    {"id": 10, "category": "Team",   "image": "Gallery/team-group.jpg",        "label": "The Bright Bean team"},
    {"id": 11, "category": "Food",   "image": "Gallery/chocolate-cake.jpg",    "label": "Chocolate drip cake"},
    {"id": 12, "category": "Events", "image": "Gallery/tasting-event.jpg",     "label": "Coffee tasting event"},
    {"id": 13, "category": "Café",   "image": "Gallery/patio-lights.jpg",      "label": "String lights on the patio"},
    {"id": 14, "category": "Coffee", "image": "Gallery/cappuccino-close.jpg",  "label": "Cappuccino foam art"},
    {"id": 15, "category": "Events", "image": "Gallery/friends-table.jpg",     "label": "Friends catching up"},
]
