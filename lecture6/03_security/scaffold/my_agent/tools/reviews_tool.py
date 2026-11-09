"""Local reviews tool — user-generated content, i.e. UNTRUSTED data.

The reviews come from a JSON file to keep the demo offline and reproducible.
In production this would be a web scrape or a review API: anyone can write a
review, so anyone can put text in front of your LLM. One Salzburg review
contains an indirect prompt injection.
"""

import json
from pathlib import Path
from typing import Any, Dict

_REVIEWS_FILE = Path(__file__).resolve().parents[1] / "data" / "reviews.json"


def get_local_reviews(city: str) -> Dict[str, Any]:
    """Return recent visitor reviews of places in a city.

    Args:
        city: City name, e.g. "Salzburg".

    Returns:
        Dict with the city and a list of reviews (place, rating 1-5, text).
    """
    reviews = json.loads(_REVIEWS_FILE.read_text(encoding="utf-8"))
    return {"city": city, "reviews": reviews.get(city.strip().lower(), [])}
