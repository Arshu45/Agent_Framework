"""
Central configuration for the entire system.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"  # Free model


# LLM Settings
TEMPERATURE = 0.3
MAX_TOKENS = 2048

# Intent Classification
INTENT_CLASSES = ["SEARCH", "REFINE", "CLARIFY", "CHITCHAT"]

# Filter Extraction - Vague term mappings
VAGUE_TERMS = {
    "cheap": {"price_max": 50},
    "affordable": {"price_max": 100},
    "expensive": {"price_min": 500},
    "premium": {"price_min": 300},
    "budget": {"price_max": 75},
    "high-end": {"price_min": 400},
    "top-rated": {"rating_min": 4.5},
    "best": {"rating_min": 4.0},
}

# Context Settings
MAX_CONVERSATION_HISTORY = 10
MAX_RECOMMENDATIONS = 5

# File Paths
PROMPTS_DIR = "prompts"
DATA_DIR = "data"
MOCK_PRODUCTS_FILE = f"{DATA_DIR}/mock_products.json"

