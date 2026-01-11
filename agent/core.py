"""
Core Agent Module - Main orchestration
"""
from typing import Dict
from agent.intent_classifier import IntentClassifier
from agent.filter_extractor import FilterExtractor
from agent.prompt_builder import PromptBuilder
from agent.llm_client import LLMClient
from agent.context_manager import ContextManager
from agent.product_retriever import ProductRetriever

import config


class AgentResponse:
    """Structured agent response"""
    def __init__(self, recommendations: list, summary: str, intent: str, filters: dict, 
                 follow_up_questions: list = None):
        self.recommendations = recommendations
        self.summary = summary
        self.intent = intent
        self.filters = filters
        self.follow_up_questions = follow_up_questions or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "recommendations": self.recommendations,
            "summary": self.summary,
            "intent": self.intent,
            "filters": self.filters,
            "follow_up_questions": self.follow_up_questions
        }


class Agent:
    """Main agent orchestrator"""
    
    def __init__(self, product_retriever=None):
        self.intent_classifier = IntentClassifier()
        self.filter_extractor = FilterExtractor()
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()
        self.context_manager = ContextManager()
        # Use provided retriever or default to API retriever
        self.product_retriever = product_retriever or ProductRetriever()
    
    def process(self, user_query: str) -> AgentResponse:
        """
        Main processing method - orchestrates all agent logic
        
        Args:
            user_query: Current user query
            
        Returns:
            AgentResponse with recommendations and metadata
        """
        print(f"\n{'='*60}")
        print(f"Processing query: {user_query}")
        print(f"{'='*60}\n")
        
        # 1. Intent Classification
        print("Step 1: Classifying intent...")
        history = self.context_manager.get_history()
        intent_result = self.intent_classifier.classify(user_query, history)
        intent = intent_result["intent"]
        print(f"Intent: {intent} (confidence: {intent_result['confidence']:.2f})")
        
        # 2. Filter Extraction
        print("\nStep 2: Extracting filters...")
        existing_filters = self.context_manager.get_filters()
        filters = self.filter_extractor.extract(user_query, history, existing_filters)
        print(f"Extracted filters: {filters}")
        
        # 3. Context Update
        print("\nStep 3: Updating context...")
        if intent == "REFINE":
            # Merge filters for refinement
            self.context_manager.update_filters(filters)
        elif intent == "SEARCH":
            # New search - clear and set filters
            self.context_manager.clear_filters()
            self.context_manager.update_filters(filters)
        # CLARIFY and CHITCHAT don't update filters
        
        updated_filters = self.context_manager.get_filters()
        print(f"Updated filters: {updated_filters}")
        
        # 4. Retrieve products from retriever (API/RAG)
        print("\nStep 4a: Retrieving products...")
        retrieved_products = self.product_retriever.retrieve(
            query=user_query,
            filters=updated_filters,
            top_k=10
        )
        print(f"Retrieved {len(retrieved_products)} products")
        
        # Update LLM client's product catalog for validation
        if retrieved_products:
            self.llm_client.update_product_catalog(retrieved_products)
        
        # 4b. Prompt Building
        print("\nStep 4b: Building prompt...")
        prompt = self.prompt_builder.build(
            user_query, 
            history, 
            updated_filters,
            products=retrieved_products  # Pass retrieved products
        )
        print(f"Prompt length: {len(prompt)} characters")
        
        # 5. LLM Call & Parsing
        print("\nStep 5: Calling LLM...")
        llm_response = self.llm_client.get_recommendations(prompt)
        
        # Filter out rejected products
        rejected_ids = self.context_manager.get_rejected_ids()
        filtered_recs = [
            rec for rec in llm_response["recommendations"]
            if rec["product_id"] not in rejected_ids
        ]
        
        # If all recommendations were rejected, use original
        if not filtered_recs:
            filtered_recs = llm_response["recommendations"]
        
        # 6. Update context with agent response
        agent_response_text = llm_response["summary"]
        self.context_manager.add_turn(user_query, agent_response_text)
        
        # 7. Return structured response
        print("\nStep 6: Returning response...")
        response = AgentResponse(
            recommendations=filtered_recs,
            summary=llm_response["summary"],
            intent=intent,
            filters=updated_filters,
            follow_up_questions=llm_response.get("follow_up_questions", [])
        )
        
        print(f"\n{'='*60}")
        print("Processing complete!")
        print(f"{'='*60}\n")
        
        return response
    
    def reset_session(self):
        """Reset conversation session"""
        self.context_manager.reset()
        print("Session reset.")

