"""
Intent Classification Module
"""
import json
from typing import Dict, List
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

import config


class IntentOutput(BaseModel):
    """Structured output for intent classification"""
    intent: str = Field(description="Intent type: SEARCH, REFINE, CLARIFY, or CHITCHAT")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")


class IntentClassifier:
    """Classifies user intent from query and conversation history"""
    
    # Creating the LLM client and parser
    def __init__(self):
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            temperature=config.TEMPERATURE,
            groq_api_key=config.GROQ_API_KEY
        )
        self.parser = PydanticOutputParser(pydantic_object=IntentOutput)
        
        # Load prompt template
        with open(f"{config.PROMPTS_DIR}/intent_classification.txt", "r") as f:
            template = f.read()
        
        self.prompt_template = PromptTemplate(
            template=template,
            input_variables=["query", "conversation_history"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
    
    # Classifying the intent using the LLM client and parser
    def classify(self, query: str, conversation_history: List[Dict]) -> Dict:
        """
        Classify user intent
        
        Args:
            query: Current user query
            conversation_history: List of previous conversation turns
            
        Returns:
            Dict with 'intent' and 'confidence' keys
        """
        # Format conversation history
        history_str = self._format_history(conversation_history)
        
        # Build prompt
        prompt = self.prompt_template.format(
            query=query,
            conversation_history=history_str
        )
        
        try:
            # Call LLM
            response = self.llm.invoke(prompt)
            
            # Parse output
            parsed = self.parser.parse(response.content)
            
            # Validate intent
            intent = parsed.intent.upper()
            if intent not in config.INTENT_CLASSES:
                intent = "SEARCH"  # Fallback
            
            return {
                "intent": intent,
                "confidence": max(0.0, min(1.0, parsed.confidence))
            }
        except Exception as e:
            # Fallback: simple heuristic
            print(f"Intent classification error: {e}")
            return self._fallback_classify(query, conversation_history)
    
    def _format_history(self, history: List[Dict]) -> str:
        """Format conversation history for prompt"""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for i, turn in enumerate(history[-3:], 1):  # Last 3 turns
            user_msg = turn.get("user", "")
            agent_msg = turn.get("agent", "")
            formatted.append(f"Turn {i}:\nUser: {user_msg}\nAgent: {agent_msg}")
        
        return "\n\n".join(formatted)
    
    def _fallback_classify(self, query: str, history: List[Dict]) -> Dict:
        """Simple heuristic fallback"""
        query_lower = query.lower()
        
        # Check for greetings/chitchat
        greetings = ["hello", "hi", "hey", "thanks", "thank you"]
        if any(g in query_lower for g in greetings):
            return {"intent": "CHITCHAT", "confidence": 0.7}
        
        # Check for clarification questions
        clarify_words = ["what", "how", "why", "explain", "tell me"]
        if any(cw in query_lower for cw in clarify_words) and "?" in query:
            return {"intent": "CLARIFY", "confidence": 0.6}
        
        # Check for refinement keywords
        refine_words = ["also", "and", "but", "except", "not", "without"]
        if any(rw in query_lower for rw in refine_words) and history:
            return {"intent": "REFINE", "confidence": 0.6}
        
        # Default to search
        return {"intent": "SEARCH", "confidence": 0.5}

