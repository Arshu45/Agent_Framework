"""
Filter Extraction Module (Story 2)
"""
import json
import re
from typing import Dict, List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

import config


class FilterOutput(BaseModel):
    """Structured output for filter extraction"""
    price_min: Optional[float] = Field(default=None, description="Minimum price")
    price_max: Optional[float] = Field(default=None, description="Maximum price")
    brand_include: Optional[List[str]] = Field(default=None, description="Brands to include")
    brand_exclude: Optional[List[str]] = Field(default=None, description="Brands to exclude")
    category: Optional[str] = Field(default=None, description="Product category")
    features: Optional[List[str]] = Field(default=None, description="Required features")
    rating_min: Optional[float] = Field(default=None, description="Minimum rating")


class FilterExtractor:
    """Extracts structured filters from user queries"""
    # Creating the LLM client and parser
    def __init__(self):
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            temperature=config.TEMPERATURE,
            groq_api_key=config.GROQ_API_KEY
        )
        self.parser = PydanticOutputParser(pydantic_object=FilterOutput)
        
        # Load prompt template
        with open(f"{config.PROMPTS_DIR}/filter_extraction.txt", "r") as f:
            template = f.read()
        
        self.prompt_template = PromptTemplate(
            template=template,
            input_variables=["query", "conversation_history", "existing_filters", "vague_terms"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
    
    # Extracting the filters using the LLM client and parser
    def extract(self, query: str, conversation_history: List[Dict], 
                existing_filters: Optional[Dict] = None) -> Dict:
        """
        Extract filters from query
        
        Args:
            query: Current user query
            conversation_history: List of previous conversation turns
            existing_filters: Previously extracted filters (may be overridden)
            
        Returns:
            Dict with filter keys (price_min, price_max, etc.)
        """
        existing_filters = existing_filters or {}
        history_str = self._format_history(conversation_history)
        vague_terms_str = json.dumps(config.VAGUE_TERMS, indent=2)
        
        # Build prompt
        prompt = self.prompt_template.format(
            query=query,
            conversation_history=history_str,
            existing_filters=json.dumps(existing_filters, indent=2),
            vague_terms=vague_terms_str
        )
        
        try:
            # Call LLM
            response = self.llm.invoke(prompt)
            
            # Parse output
            parsed = self.parser.parse(response.content)
            
            # Convert to dict and clean
            filters = {
                "price_min": parsed.price_min,
                "price_max": parsed.price_max,
                "brand_include": parsed.brand_include or [],
                "brand_exclude": parsed.brand_exclude or [],
                "category": parsed.category,
                "features": parsed.features or [],
                "rating_min": parsed.rating_min
            }
            
            # Apply vague term mappings
            filters = self._apply_vague_terms(query, filters)
            
            # Merge with existing filters (new filters override)
            merged = self._merge_filters(existing_filters, filters)
            
            return merged
            
        except Exception as e:
            # Fallback: regex extraction
            print(f"Filter extraction error: {e}")
            return self._regex_extract(query, existing_filters)
    
    def _format_history(self, history: List[Dict]) -> str:
        """Format conversation history for prompt"""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for i, turn in enumerate(history[-3:], 1):
            user_msg = turn.get("user", "")
            formatted.append(f"Turn {i}: {user_msg}")
        
        return "\n".join(formatted)
    
    def _apply_vague_terms(self, query: str, filters: Dict) -> Dict:
        """Apply vague term mappings"""
        query_lower = query.lower()
        
        for term, mapping in config.VAGUE_TERMS.items():
            if term in query_lower:
                if "price_max" in mapping and filters.get("price_max") is None:
                    filters["price_max"] = mapping["price_max"]
                if "price_min" in mapping and filters.get("price_min") is None:
                    filters["price_min"] = mapping["price_min"]
                if "rating_min" in mapping and filters.get("rating_min") is None:
                    filters["rating_min"] = mapping["rating_min"]
        
        return filters
    
    def _merge_filters(self, existing: Dict, new: Dict) -> Dict:
        """Merge filters deterministically (new overrides existing)"""
        merged = existing.copy()
        
        for key, value in new.items():
            if value is not None:
                if key in ["brand_include", "brand_exclude", "features"]:
                    # Merge lists
                    existing_list = merged.get(key, []) or []
                    new_list = value or []
                    merged[key] = list(set(existing_list + new_list))
                else:
                    # Override
                    merged[key] = value
        
        return merged
    
    def _regex_extract(self, query: str, existing_filters: Dict) -> Dict:
        """Regex-based fallback extraction"""
        filters = existing_filters.copy()
        query_lower = query.lower()
        
        # Extract price ranges
        price_pattern = r'\$?(\d+(?:\.\d+)?)'
        prices = re.findall(price_pattern, query)
        if prices:
            prices = [float(p) for p in prices]
            if "under" in query_lower or "less than" in query_lower or "below" in query_lower:
                filters["price_max"] = min(prices)
            elif "over" in query_lower or "more than" in query_lower or "above" in query_lower:
                filters["price_min"] = max(prices)
            elif len(prices) == 1:
                filters["price_max"] = prices[0]
        
        # Extract rating
        rating_pattern = r'(\d+(?:\.\d+)?)\s*(?:star|rating)'
        ratings = re.findall(rating_pattern, query_lower)
        if ratings:
            filters["rating_min"] = float(ratings[0])
        
        return filters

