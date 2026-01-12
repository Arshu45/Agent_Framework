"""
RAG Retriever - Integrates team lead's retriever logic with agent
Wraps retriever.py functionality without modifying it
"""
import os
import json
import re
import time
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq
from groq import APIConnectionError, RateLimitError, InternalServerError
from typing import Dict, List

import config


class RAGRetriever:
    """
    RAG Retriever that uses ChromaDB vector search
    Integrates retriever.py logic with agent interface
    """
    
    def __init__(self):
        """Initialize ChromaDB and Groq clients"""
        load_dotenv()
        
        # ChromaDB config
        self.db_dir = os.path.abspath(os.getenv("CHROMA_DB_DIR", ""))
        self.collection_name = os.getenv("COLLECTION_NAME", "")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "")
        
        if not self.db_dir or not self.collection_name or not self.embedding_model:
            raise ValueError("Missing ChromaDB env variables: CHROMA_DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL")
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.db_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        
        # Initialize Groq for attribute extraction
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key:
            raise ValueError("GROQ_API_KEY not found in .env")
        
        self.groq_client = Groq(api_key=groq_key)
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    def retrieve(self, query: str, filters: Dict = None, top_k: int = 10) -> List[Dict]:
        """
        Retrieve products using RAG (vector search + metadata filtering)
        
        Args:
            query: User query string
            filters: Agent-extracted filters (will be converted to ChromaDB format)
            top_k: Number of products to return
        
        Returns:
            List of product dicts in agent format
        """
        try:
            # 1. Query rewriting (from retriever.py)
            rewritten_query = self._rewrite_query(query)
            print(f"  [RAG] Rewritten query: {rewritten_query}")
            
            # 2. Extract attributes from query (from retriever.py)
            raw_filters = self._extract_attributes(query)
            print(f"  [RAG] LLM-extracted filters: {raw_filters}")
            
            # 3. Merge agent filters with extracted filters
            chroma_filters = self._build_chroma_filters(raw_filters, filters)
            print(f"  [RAG] ChromaDB filters: {chroma_filters}")
            
            # Check collection count
            collection_count = self.collection.count()
            print(f"  [RAG] Collection has {collection_count} products")
            
            # 4. Vector search + metadata filter
            results = self.collection.query(
                query_texts=[rewritten_query],
                n_results=top_k,
                where=chroma_filters if chroma_filters else None
            )
            
            # Debug: Check raw results
            if results.get("documents") and results["documents"][0]:
                print(f"  [RAG] ChromaDB returned {len(results['documents'][0])} raw results")
            else:
                print(f"  [RAG] ChromaDB returned 0 raw results")
                # Try without filters to see if filters are too strict
                if chroma_filters:
                    print(f"  [RAG] Trying without filters to check if filters are too strict...")
                    results_no_filter = self.collection.query(
                        query_texts=[rewritten_query],
                        n_results=top_k,
                        where=None
                    )
                    if results_no_filter.get("documents") and results_no_filter["documents"][0]:
                        print(f"  [RAG] Without filters: {len(results_no_filter['documents'][0])} results found")
                        # Use results without filters as fallback
                        results = results_no_filter
            
            # 5. Transform ChromaDB results to agent format
            products = self._transform_results(results)
            print(f"  [RAG] Transformed to {len(products)} products")
            
            return products
            
        except Exception as e:
            print(f"RAG retrieval error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _rewrite_query(self, user_query: str) -> str:
        """Rewrite query for semantic search (from retriever.py)"""
        # For now, return as-is (can be enhanced with LLM later)
        return user_query.strip()
    
    def _extract_attributes(self, user_query: str) -> Dict:
        """Extract attributes from query using LLM (from retriever.py)"""
        prompt_template = os.getenv("EXTRACT_ATTRIBUTES_SYSTEM_PROMPT")
        if not prompt_template:
            # Fallback: return empty dict if prompt not configured
            return {}
        
        max_retries = 3
        sleep_seconds = 3
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    temperature=0,
                    messages=[
                        {"role": "system", "content": prompt_template},
                        {"role": "user", "content": user_query}
                    ]
                )
                
                raw = response.choices[0].message.content.strip()
                return json.loads(raw)
                
            except (APIConnectionError, RateLimitError, InternalServerError) as e:
                last_error = e
                print(f"[Retry {attempt}/{max_retries}] Groq error: {e}")
                if attempt < max_retries:
                    time.sleep(sleep_seconds)
                else:
                    break
                    
            except json.JSONDecodeError:
                # Try to extract JSON from response
                try:
                    return self._safe_json_loads(raw)
                except:
                    raise ValueError(f"Invalid JSON returned:\n{raw}")
                    
            except Exception as e:
                raise RuntimeError(f"Unexpected error: {e}")
        
        raise RuntimeError(f"Groq API failed after {max_retries} attempts: {last_error}")
    
    def _safe_json_loads(self, text: str) -> dict:
        """Safely extract JSON from LLM output (from retriever.py)"""
        text = text.strip()
        
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text)
            text = re.sub(r"```$", "", text)
            text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in response")
        
        json_str = match.group()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON:\n{json_str}") from e
    
    def _build_chroma_filters(self, raw_filters: Dict, agent_filters: Dict = None) -> Dict:
        """
        Build ChromaDB where filter from extracted attributes and agent filters
        Combines retriever.py filter building logic
        """
        filters = []
        
        # Add filters from LLM extraction (retriever.py logic)
        for key, value in raw_filters.items():
            if value is None:
                continue
            
            # Age handling (from retriever.py)
            if key == "age":
                if "$gte" in value and "$lte" in value:
                    filters.append({"age_max": {"$lte": value["$lte"]}})
                    filters.append({"age_min": {"$gte": value["$gte"]}})
                elif "$eq" in value:
                    age = value["$eq"]
                    filters.append({"age_min": {"$lte": age}})
                    filters.append({"age_max": {"$gte": age}})
                elif "$lt" in value:
                    filters.append({"age_min": {"$lt": value["$lt"]}})
                elif "$gt" in value:
                    filters.append({"age_max": {"$gt": value["$gt"]}})
                continue
            
            if isinstance(value, dict):
                for op, num in value.items():
                    filters.append({key: {op: num}})
            else:
                normalized = value.strip().lower() if isinstance(value, str) else value
                filters.append({key: normalized})
        
        # Add filters from agent (convert agent format to ChromaDB format)
        if agent_filters:
            # Price filters
            if agent_filters.get("price_min"):
                filters.append({"price": {"$gte": agent_filters["price_min"]}})
            if agent_filters.get("price_max"):
                filters.append({"price": {"$lte": agent_filters["price_max"]}})
            
            # Category filter
            if agent_filters.get("category"):
                filters.append({"category": agent_filters["category"].lower()})
            
            # Brand filters (ChromaDB format - single brand or first brand)
            if agent_filters.get("brand_include"):
                # Use first brand (ChromaDB where clause format)
                first_brand = agent_filters["brand_include"][0].lower()
                filters.append({"brand": first_brand})
            
            if agent_filters.get("brand_exclude"):
                # Note: ChromaDB doesn't support $ne easily, might need to filter post-query
                pass  # Skip for now, can filter after retrieval
            
            # Rating filter
            if agent_filters.get("rating_min"):
                filters.append({"rating": {"$gte": agent_filters["rating_min"]}})
        
        # Build final ChromaDB where clause
        if not filters:
            return None
        elif len(filters) == 1:
            return filters[0]
        else:
            return {"$and": filters}
    
    def _normalize_filter_value(self, val):
        """Normalize filter value (from retriever.py)"""
        if isinstance(val, str):
            return val.strip().lower()
        return val
    
    def _transform_results(self, results: Dict) -> List[Dict]:
        """
        Transform ChromaDB results to agent product format
        
        ChromaDB returns:
        - documents: List of JSON strings
        - metadatas: List of metadata dicts
        - ids: List of product IDs
        
        Agent expects:
        - id, name, category, brand, price, rating, features
        """
        products = []
        
        if not results.get("documents") or not results["documents"][0]:
            return products
        
        documents = results["documents"][0]
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(documents)
        ids = results["ids"][0] if results.get("ids") else [f"prod_{i}" for i in range(len(documents))]
        
        for i, doc_json in enumerate(documents):
            try:
                # Parse document JSON
                doc = json.loads(doc_json) if isinstance(doc_json, str) else doc_json
                metadata = metadatas[i] if i < len(metadatas) else {}
                product_id = ids[i] if i < len(ids) else f"prod_{i}"
                
                # Extract fields (adapt based on your actual document structure)
                # Common fields: name/title, category, brand, price, rating, description
                product = {
                    "id": str(product_id),
                    "name": doc.get("name") or doc.get("title") or doc.get("product_name") or "Unknown Product",
                    "category": metadata.get("category") or doc.get("category") or "General",
                    "brand": metadata.get("brand") or doc.get("brand") or "Unknown Brand",
                    "price": float(metadata.get("price") or doc.get("price") or 0),
                    "rating": float(metadata.get("rating") or doc.get("rating") or 0),
                    "features": self._extract_features_from_doc(doc, metadata),
                    "description": doc.get("description") or ""
                }
                
                products.append(product)
                
            except Exception as e:
                print(f"Error transforming product {i}: {e}")
                continue
        
        return products
    
    def _extract_features_from_doc(self, doc: Dict, metadata: Dict) -> List[str]:
        """Extract features from document and metadata"""
        features = []
        
        # Add category as feature
        category = metadata.get("category") or doc.get("category")
        if category:
            features.append(category.lower().replace(" ", "-"))
        
        # Extract from description
        description = (doc.get("description") or "").lower()
        common_features = [
            "wireless", "bluetooth", "portable", "waterproof",
            "noise cancellation", "gaming", "smart", "led",
            "battery", "rechargeable"
        ]
        
        for feat in common_features:
            if feat in description:
                features.append(feat)
        
        return features

