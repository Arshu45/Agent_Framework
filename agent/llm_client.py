"""
LLM Client Module (Story 4)
"""
import json
import re
from typing import Dict, List
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

import config


class RecommendationItem(BaseModel):
    """Single recommendation item"""
    product_id: str = Field(description="Product ID")
    product_name: str = Field(description="Product Name")
    reasoning: str = Field(description="Reasoning for recommendation")


class RecommendationOutput(BaseModel):
    """Structured output for recommendations"""
    recommendations: List[RecommendationItem] = Field(description="List of recommendations")
    summary: str = Field(description="Summary of recommendations")
    follow_up_questions: List[str] = Field(default=[], description="Suggested follow-up questions for the user")


class LLMClient:
    """Handles LLM interactions and response parsing"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            groq_api_key=config.GROQ_API_KEY
        )
        # Start with empty catalog; updated by retrievers at runtime
        self.valid_product_ids: set = set()
        self.product_lookup: Dict = {}
    
    def _load_product_catalog(self, products: List[Dict] = None):
        """Load product catalog for validation and lookup"""
        products = products or []
        self.valid_product_ids = {p.get("id") for p in products if p.get("id")}
        self.product_lookup = {p["id"]: p for p in products if p.get("id")}  # For quick name lookup
    
    def update_product_catalog(self, products: List[Dict]):
        """Update product catalog (e.g., from retriever)"""
        self._load_product_catalog(products)
    
    def get_recommendations(self, prompt: str, max_retries: int = 2) -> Dict:
        """
        Get product recommendations from LLM
        
        Args:
            prompt: Complete recommendation prompt
            max_retries: Maximum retry attempts
            
        Returns:
            Dict with 'recommendations' and 'summary' keys
        """
        for attempt in range(max_retries + 1):
            try:
                print(f"LLM call attempt {attempt + 1}...")
                
                # Call LLM
                response = self.llm.invoke(prompt)
                content = response.content
                
                # Extract JSON from response
                json_str = self._extract_json(content)
                
                # Parse JSON
                parsed = json.loads(json_str)
                
                # Validate structure
                validated = self._validate_response(parsed)
                
                print(f"Successfully parsed {len(validated['recommendations'])} recommendations")
                return validated
                
            except Exception as e:
                print(f"LLM call error (attempt {attempt + 1}): {e}")
                if attempt == max_retries:
                    # Final fallback
                    return self._fallback_response()
        
        return self._fallback_response()
    
    def _extract_json(self, content: str) -> str:
        """Extract JSON from LLM response"""
        # Try to find JSON block
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json_match.group(0)
        
        # If no JSON found, try to parse entire content
        return content.strip()
    
    def _validate_response(self, parsed: Dict) -> Dict:
        """Validate and clean response"""
        recommendations = []
        
        # Extract recommendations
        recs = parsed.get("recommendations", [])
        if isinstance(recs, list):
            for rec in recs[:config.MAX_RECOMMENDATIONS]:
                if isinstance(rec, dict):
                    product_id = rec.get("product_id", "")
                    reasoning = rec.get("reasoning", "")
                    product_name = rec.get("product_name", "")
                    
                    # If we have a catalog, ensure the ID exists; otherwise accept as-is
                    id_is_valid = (not self.valid_product_ids) or (product_id in self.valid_product_ids)
                    if not id_is_valid:
                        continue
                    
                    # If product_name not provided, look it up from product data
                    if not product_name and product_id in self.product_lookup:
                        product_name = self.product_lookup[product_id].get("name", "")
                    
                    recommendations.append({
                        "product_id": product_id or "unknown_id",
                        "product_name": product_name or "Unknown Product",
                        "reasoning": reasoning or "Recommended based on your preferences"
                    })
        
        # Ensure at least one recommendation
        if not recommendations:
            # If we have a catalog, use the first product as fallback; otherwise return empty
            if self.valid_product_ids:
                first_id = list(self.valid_product_ids)[0]
                first_product = self.product_lookup.get(first_id, {})
                recommendations.append({
                    "product_id": first_id,
                    "product_name": first_product.get("name", "Unknown Product"),
                    "reasoning": "Fallback recommendation"
                })
        
        # Extract follow-up questions
        follow_up_questions = parsed.get("follow_up_questions", [])
        if isinstance(follow_up_questions, list):
            # Ensure all items are strings and limit to 3 questions
            follow_up_questions = [
                str(q).strip() for q in follow_up_questions[:3] 
                if q and str(q).strip()
            ]
        else:
            follow_up_questions = []
        
        return {
            "recommendations": recommendations,
            "summary": parsed.get("summary", "Product recommendations based on your query"),
            "follow_up_questions": follow_up_questions
        }
    
    def _fallback_response(self) -> Dict:
        """Graceful fallback response"""
        print("Using fallback response")
        if self.valid_product_ids:
            first_id = list(self.valid_product_ids)[0]
            first_product = self.product_lookup.get(first_id, {})
            recommendations = [{
                "product_id": first_id,
                "product_name": first_product.get("name", "Unknown Product"),
                "reasoning": "Fallback recommendation due to processing error"
            }]
        else:
            recommendations = []
        return {
            "recommendations": recommendations,
            "summary": "Unable to process request fully.",
            "follow_up_questions": [
                "Would you like to see more options?",
                "Do you have a specific budget in mind?",
                "Are there any particular features you're looking for?"
            ]
        }

