"""
Product Retriever Tool - RAG-Compatible Retriever (Electronics Only)

Acts as a thin adapter that returns product context to the agent.

IMPORTANT:
- Semantic search is handled by RAG (vector DB)
- Metadata filtering is handled by RAG
- This retriever ONLY fetches and normalizes data
- Electronics are aggregated from multiple DummyJSON categories
"""

import requests
import json
from typing import Dict, List

import config


class ProductRetriever:
    """
    Thin retriever adapter.

    In production:
    - This will be replaced by a real RAG retriever (vector DB).
    - No filtering or scoring should exist here.
    - The agent receives already-filtered, already-ranked results.
    """

    # DummyJSON electronics-related categories
    ELECTRONICS_CATEGORIES = [
        # "smartphones",
        "laptops"
        # "Televisions",
        # "Headphones"
        # You can add later:
        # "mobile-accessories",
        # "tablets"
    ]

    def __init__(self):
        self.api_base_url = "https://dummyjson.com"
        self.session = requests.Session()
        self.session.timeout = 5

    def retrieve(self, query: str, filters: Dict = None, top_k: int = 10) -> List[Dict]:
        """
        Retrieve electronic products for agent context.

        NOTE:
        - `query` and `filters` are accepted only to match RAG retriever interface
        - They are NOT used here (RAG handles them upstream)

        Args:
            query: User query (ignored here)
            filters: Metadata filters (ignored here)
            top_k: Number of products to return

        Returns:
            List of normalized electronic product dictionaries
        """
        try:
            products = self._fetch_electronics()

            # RAG would already rank; we just cap results
            return products[:top_k]

        except Exception as e:
            print(f"Product retrieval error: {e}")
            return self._fallback_products()

    def _fetch_electronics(self) -> List[Dict]:
        """Fetch and normalize electronic products from DummyJSON"""
        all_products: List[Dict] = []

        try:
            for category in self.ELECTRONICS_CATEGORIES:
                url = f"{self.api_base_url}/products/category/{category}"
                response = self.session.get(url)
                response.raise_for_status()

                api_products = response.json().get("products", [])
                print(api_products)

                for p in api_products:
                    all_products.append({
                        "id": f"dummy_{p['id']}",
                        "name": p.get("title", "Unknown Product"),
                        "category": category,
                        "brand": p.get("brand", "Unknown Brand"),
                        "price": float(p.get("price", 0)),
                        "rating": float(p.get("rating", 0)),
                        "features": self._extract_features(p, category),
                        "description": p.get("description", "")
                    })

            return all_products

        except Exception as e:
            print(f"Electronics API fetch error: {e}")
            return []

    def _extract_features(self, product: Dict, category: str) -> List[str]:
        """
        Light feature extraction to enrich context for the agent.
        This does NOT affect filtering or ranking.
        """
        features = ["electronics", category]

        description = product.get("description", "").lower()

        common_features = [
            "wireless", "bluetooth", "portable", "waterproof",
            "noise cancellation", "gaming", "smart", "led",
            "battery", "rechargeable"
        ]

        for feat in common_features:
            if feat in description:
                features.append(feat)

        return features

    def _fallback_products(self) -> List[Dict]:
        """Fallback to local mock products if API fails"""
        try:
            with open(config.MOCK_PRODUCTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
