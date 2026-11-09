"""City notes RAG tool — local embeddings (sentence-transformers) + Chroma.

Lecture 5 · Section 2: Add Persistence · SOLUTION
─────────────────────────────────────────────────
Companion to the weather tool. Shows how retrieval-augmented generation (RAG)
sits next to session persistence:

  session state     (ToolContext)                      → short-term memory
  vector store      (Chroma + sentence-transformers)   → long-term knowledge

Why local embeddings instead of a hosted API?
  - RAG works with any chat LLM. Using Lion (Qwen) for chat + Gemini for
    embeddings would mix two providers; local embeddings keep the course
    offline-capable and avoid a second API key.
  - `all-MiniLM-L6-v2` is ~80 MB, downloaded once from HuggingFace on first use
    and cached under `~/.cache/huggingface/`.

Pipeline:
  1. On first tool call, read `../city_notes/*.md`, split each file on blank
     lines into paragraph-sized chunks, and `add` them to an in-memory Chroma
     collection. Chroma asks sentence-transformers for a 384-dim vector per
     chunk (CPU, a few milliseconds each).
  2. On query, Chroma embeds the query with the same function and returns the
     top-k nearest chunks by cosine distance, filtered by the city metadata.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from google.adk.tools.tool_context import ToolContext


_NOTES_DIR = Path(__file__).resolve().parents[2] / "city_notes"
_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
_KNOWN_CITIES = sorted({p.stem.lower() for p in _NOTES_DIR.glob("*.md")})


@lru_cache(maxsize=1)
def _embedder() -> SentenceTransformerEmbeddingFunction:
    """Load the sentence-transformers model once. First call downloads it (~80 MB)
    from HuggingFace and caches under ~/.cache/huggingface/."""
    return SentenceTransformerEmbeddingFunction(
        model_name=_EMBEDDING_MODEL,
        normalize_embeddings=True,  # unit vectors → cosine distance via dot product
    )


@lru_cache(maxsize=1)
def _collection():
    """Build (or return cached) in-memory Chroma collection. Lazy so adk web
    boots instantly; the model loads and the corpus is embedded on first query."""
    client = chromadb.Client()
    coll = client.get_or_create_collection(
        "city_notes",
        embedding_function=_embedder(),
    )
    if coll.count() > 0:
        return coll

    docs, metas, ids = [], [], []
    for md_file in sorted(_NOTES_DIR.glob("*.md")):
        city = md_file.stem.lower()
        chunks = [c.strip() for c in md_file.read_text(encoding="utf-8").split("\n\n")]
        for i, chunk in enumerate(c for c in chunks if c):
            docs.append(chunk)
            metas.append({"city": city, "source": md_file.name})
            ids.append(f"{city}-{i}")
    if docs:
        coll.add(documents=docs, metadatas=metas, ids=ids)
    return coll


def retrieve_city_notes(
    city: str,
    query: str = "",
    top_k: int = 3,
    tool_context: ToolContext = None,
) -> Dict[str, Any]:
    """Retrieve relevant travel notes about a city via semantic (vector) search
    over a local knowledge base.

    Use this when the user asks for things the weather tool cannot answer:
    cheap eats, transit, student discounts, rainy-day options, nightlife, day trips.

    Args:
        city: City name to scope the search (e.g. "Vienna"). Case-insensitive.
        query: What the user wants to know (e.g. "cheap student activities").
               Defaults to the city name alone when empty.
        top_k: Maximum number of passages to return (1-10, default 3).

    Returns:
        Dict with the resolved city, the query used, and a list of matches
        where each match has a `snippet` (the passage), `source` (the file),
        and `distance` (cosine distance, lower = more similar).
    """
    top_k = max(1, min(top_k, 10))
    city_key = city.strip().lower()
    search_text = (query or city).strip()

    if city_key not in _KNOWN_CITIES:
        return {
            "city": city,
            "query": query,
            "matches": [],
            "error": f"No notes for {city!r}. Known cities: {_KNOWN_CITIES}",
        }

    results = _collection().query(
        query_texts=[search_text],
        n_results=top_k,
        where={"city": city_key},
    )
    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]
    matches = [
        {
            "snippet": doc,
            "source": (meta or {}).get("source", "?"),
            "distance": round(float(dist), 3),
        }
        for doc, meta, dist in zip(docs, metas, distances)
    ]

    if tool_context is not None:
        tool_context.state["last_retrieved_notes"] = {
            "city": city,
            "query": search_text,
            "snippet_count": len(matches),
        }

    return {"city": city, "query": search_text, "matches": matches}
