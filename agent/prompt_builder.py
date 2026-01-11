"""
Prompt Builder Module
"""
import json
from typing import Dict, List

import config


class PromptBuilder:
    """Builds final recommendation prompts"""
    
    def __init__(self):
        # Load system prompt
        with open(f"{config.PROMPTS_DIR}/system_prompt.txt", "r") as f:
            self.system_prompt = f.read()
        
        # Load mock products
        with open(config.MOCK_PRODUCTS_FILE, "r") as f:
            self.all_products = json.load(f)
    
    def build(self, query: str, conversation_history: List[Dict], 
              filters: Dict, products: List[Dict] = None) -> str:
        """
        Build final recommendation prompt
        
        Args:
            query: Current user query
            conversation_history: List of previous conversation turns
            filters: Extracted filters
            products: List of products from retriever (if None, uses rule-based)
            
        Returns:
            Complete prompt string
        """
        # 1. System prompt
        prompt_parts = [self.system_prompt]
        prompt_parts.append("\n" + "="*50 + "\n")
        
        # 2. Conversation summary (last 3 turns)
        prompt_parts.append("CONVERSATION HISTORY:")
        prompt_parts.append(self._format_conversation_summary(conversation_history))
        prompt_parts.append("\n" + "="*50 + "\n")
        
        # 3. Accumulated filters
        prompt_parts.append("USER FILTERS:")
        prompt_parts.append(self._format_filters(filters))
        prompt_parts.append("\n" + "="*50 + "\n")
        
        # 4. Product context (from retriever or rule-based)
        if products is not None:
            # Use products from retriever (RAG/API)
            # NOTE: With RAG, products are already semantically matched and filtered
            # Post-filtering here is optional (for additional refinement)
            top_products = self._apply_filters_to_products(products, filters)
        else:
            # Fallback to rule-based matching (no retriever)
            top_products = self._get_top_products(filters)
        
        prompt_parts.append("AVAILABLE PRODUCTS:")
        prompt_parts.append(self._format_products(top_products))
        prompt_parts.append("\n" + "="*50 + "\n")
        
        # 5. Current user query
        prompt_parts.append("CURRENT USER QUERY:")
        prompt_parts.append(query)
        prompt_parts.append("\n" + "="*50 + "\n")
        
        # 6. Explicit JSON output schema
        prompt_parts.append("OUTPUT FORMAT:")
        prompt_parts.append(self._get_output_schema())
        
        return "\n".join(prompt_parts)
    
    def _format_conversation_summary(self, history: List[Dict]) -> str:
        """Format conversation summary"""
        if not history:
            return "No previous conversation."
        
        summary = []
        for i, turn in enumerate(history[-3:], 1):  # Last 3 turns
            user_msg = turn.get("user", "")
            agent_msg = turn.get("agent", "")
            summary.append(f"Turn {i}:")
            summary.append(f"  User: {user_msg}")
            if agent_msg:
                summary.append(f"  Agent: {agent_msg[:100]}...")  # Truncate
        
        return "\n".join(summary)
    
    def _format_filters(self, filters: Dict) -> str:
        """Format filters for prompt"""
        filter_lines = []
        
        if filters.get("price_min"):
            filter_lines.append(f"- Minimum Price: ${filters['price_min']}")
        if filters.get("price_max"):
            filter_lines.append(f"- Maximum Price: ${filters['price_max']}")
        if filters.get("brand_include"):
            filter_lines.append(f"- Brands (include): {', '.join(filters['brand_include'])}")
        if filters.get("brand_exclude"):
            filter_lines.append(f"- Brands (exclude): {', '.join(filters['brand_exclude'])}")
        if filters.get("category"):
            filter_lines.append(f"- Category: {filters['category']}")
        if filters.get("features"):
            filter_lines.append(f"- Features: {', '.join(filters['features'])}")
        if filters.get("rating_min"):
            filter_lines.append(f"- Minimum Rating: {filters['rating_min']}")
        
        return "\n".join(filter_lines) if filter_lines else "No specific filters."
    
    def _get_top_products(self, filters: Dict, top_k: int = 10) -> List[Dict]:
        """Get top-K products matching filters"""
        matching = []
        
        for product in self.all_products:
            score = self._match_score(product, filters)
            if score > 0:
                matching.append((score, product))
        
        # Sort by score (descending) and return top-K
        matching.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in matching[:top_k]]
    
    def _match_score(self, product: Dict, filters: Dict) -> float:
        """Calculate match score for a product"""
        score = 1.0
        
        # Price filters
        if filters.get("price_min") and product["price"] < filters["price_min"]:
            return 0.0
        if filters.get("price_max") and product["price"] > filters["price_max"]:
            return 0.0
        
        # Brand filters
        if filters.get("brand_include"):
            if product["brand"] not in filters["brand_include"]:
                return 0.0
        if filters.get("brand_exclude"):
            if product["brand"] in filters["brand_exclude"]:
                return 0.0
        
        # Category filter
        if filters.get("category"):
            if filters["category"].lower() not in product["category"].lower():
                score *= 0.5
        
        # Rating filter
        if filters.get("rating_min"):
            if product["rating"] < filters["rating_min"]:
                return 0.0
        
        # Feature matching
        if filters.get("features"):
            product_features = [f.lower() for f in product.get("features", [])]
            query_features = [f.lower() for f in filters["features"]]
            matches = sum(1 for f in query_features if any(f in pf for pf in product_features))
            if matches == 0:
                score *= 0.3
            else:
                score *= (1.0 + matches * 0.2)
        
        return score
    
    def _apply_filters_to_products(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to retriever products (post-filtering)"""
        filtered = []
        for product in products:
            score = self._match_score(product, filters)
            if score > 0:
                filtered.append((score, product))
        
        # Sort by score and return
        filtered.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in filtered]
    
    def _format_products(self, products: List[Dict]) -> str:
        """Format products for prompt"""
        if not products:
            return "No products available."
        
        formatted = []
        for p in products:
            formatted.append(json.dumps(p, indent=2))
        
        return "\n\n".join(formatted)
    
    def _get_output_schema(self) -> str:
        """Get JSON output schema"""
        return """
{
  "recommendations": [
    {
      "product_id": "string",
      "product_name": "string",
      "reasoning": "string"
    }
  ],
  "summary": "string",
  "follow_up_questions": ["string"]
}

Return JSON with:
- recommendations: array of product recommendations (max 5)
- Each recommendation must have:
  - product_id: must exist in the available products
  - product_name: the name of the product (from the available products)
  - reasoning: explanation for why this product is recommended
- summary: brief explanation of recommendations
- follow_up_questions: array of 2-3 suggested follow-up questions to help the user refine their search or learn more (e.g., "Would you like to see products under $50?", "Are you looking for wireless options?", "Do you need this for a specific use case?")
"""

