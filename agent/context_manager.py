"""
Context Manager Module (Story 5)
"""
from typing import Dict, List, Set
import config


class ContextManager:
    """Manages multi-turn conversation context"""
    
    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.accumulated_filters: Dict = {}
        self.rejected_product_ids: Set[str] = set()
    
    def add_turn(self, user_query: str, agent_response: str):
        """Add a conversation turn"""
        turn = {
            "user": user_query,
            "agent": agent_response
        }
        self.conversation_history.append(turn)
        
        # Keep only last N turns
        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]
    
    # Merging the new filters with the accumulated filters
    def update_filters(self, new_filters: Dict):
        """Merge new filters with accumulated filters"""
        # The merge is deterministic (no duplicates)
        for key, value in new_filters.items():
            if value is not None:
                if key in ["brand_include", "brand_exclude", "features"]:
                    # Merge lists 
                    existing = self.accumulated_filters.get(key, []) or []
                    new_list = value if isinstance(value, list) else [value]
                    self.accumulated_filters[key] = list(set(existing + new_list))
                else:
                    # Override (new filters take precedence)
                    self.accumulated_filters[key] = value
    
    def mark_rejected(self, product_id: str):
        """Mark a product as rejected"""
        self.rejected_product_ids.add(product_id)
    
    def get_filters(self) -> Dict:
        """Get current accumulated filters"""
        return self.accumulated_filters.copy()
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def get_rejected_ids(self) -> Set[str]:
        """Get set of rejected product IDs"""
        return self.rejected_product_ids.copy()
    
    def reset(self):
        """Reset context (for new session)"""
        self.conversation_history = []
        self.accumulated_filters = {}
        self.rejected_product_ids = set()
    
    def clear_filters(self):
        """Clear accumulated filters"""
        self.accumulated_filters = {}

