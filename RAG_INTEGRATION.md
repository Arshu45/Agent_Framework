# RAG Integration Guide

## Overview

The agent now integrates with your team lead's RAG retriever (`retriver.py`) using ChromaDB vector search. The integration is seamless - **no changes were made to `retriver.py` or `ingest.py`**.

## Architecture

```
User Query
    ↓
Agent (core.py)
    ↓
1. Intent Classification
2. Filter Extraction
    ↓
RAG Retriever (rag_retriever.py)
    ↓
    ├─ Query Rewriting (from retriver.py logic)
    ├─ Attribute Extraction via LLM (from retriver.py logic)
    ├─ Filter Conversion (Agent filters → ChromaDB format)
    ├─ Vector Search + Metadata Filtering
    └─ Result Transformation (ChromaDB → Agent format)
    ↓
Products returned to Agent
    ↓
3. Prompt Building
4. LLM Recommendation
5. Response Generation
```

## Files Created

### 1. `agent/rag_retriever.py`
- **Purpose**: Wraps your retriever logic
- **Key Features**:
  - Uses ChromaDB for vector search
  - Extracts attributes using Groq LLM (same as `retriver.py`)
  - Converts agent filters to ChromaDB format
  - Transforms ChromaDB results to agent product format
- **No changes to original logic**: All logic from `retriver.py` is preserved

### 2. `examples/rag_integration_demo.py`
- Demo script showing RAG integration in action

## Usage

### Option 1: Use RAG Retriever (Recommended)

```python
from agent.core import Agent

# Initialize with RAG
agent = Agent(use_rag=True)

# Process query
response = agent.process("I need electronics under $100")
```

### Option 2: Use API Retriever (Fallback)

```python
from agent.core import Agent

# Default (uses API retriever)
agent = Agent()

# Or explicitly
agent = Agent(use_rag=False)
```

### Option 3: Custom Retriever

```python
from agent.core import Agent
from agent.rag_retriever import RAGRetriever

# Create custom retriever
retriever = RAGRetriever()

# Pass to agent
agent = Agent(product_retriever=retriever)
```

## Environment Variables Required

Make sure your `.env` file has:

```bash
# Groq API (for LLM)
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.1-8b-instant

# ChromaDB (for RAG)
CHROMA_DB_DIR=./chroma_db
COLLECTION_NAME=products
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Attribute Extraction Prompt (from retriver.py)
EXTRACT_ATTRIBUTES_SYSTEM_PROMPT=Your prompt here...
```

## Installation

Install additional dependencies:

```bash
pip install chromadb>=0.4.0 sentence-transformers>=2.2.0
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## How It Works

### 1. Filter Conversion

The agent extracts filters in this format:
```python
{
    "price_min": 50,
    "price_max": 100,
    "category": "electronics",
    "brand_include": ["Samsung", "Apple"],
    "rating_min": 4.0
}
```

The RAG retriever converts them to ChromaDB format:
```python
{
    "$and": [
        {"price": {"$gte": 50}},
        {"price": {"$lte": 100}},
        {"category": "electronics"},
        {"brand": "samsung"},
        {"rating": {"$gte": 4.0}}
    ]
}
```

### 2. Result Transformation

ChromaDB returns:
- `documents`: JSON strings (from DOCUMENT_COLUMNS)
- `metadatas`: Dict with other fields
- `ids`: Product IDs

The retriever transforms them to agent format:
```python
{
    "id": "prod_123",
    "name": "Product Name",
    "category": "electronics",
    "brand": "Samsung",
    "price": 99.99,
    "rating": 4.5,
    "features": ["wireless", "bluetooth"],
    "description": "..."
}
```

## Integration Points

### No Changes Required To:
- ✅ `retriver.py` - Original logic preserved
- ✅ `ingest.py` - Original logic preserved
- ✅ Agent core logic - Works seamlessly

### What Changed:
- ✅ Added `agent/rag_retriever.py` - New RAG adapter
- ✅ Updated `agent/core.py` - Added RAG support option
- ✅ Updated `requirements.txt` - Added chromadb, sentence-transformers

## Testing

### Test RAG Integration:

```bash
python examples/rag_integration_demo.py
```

### Test Multi-Turn with RAG:

```python
from agent.core import Agent

agent = Agent(use_rag=True)

# Turn 1
response1 = agent.process("I need electronics")

# Turn 2 (refines search)
response2 = agent.process("under $100")
```

## Troubleshooting

### Error: "Missing ChromaDB env variables"
- **Fix**: Ensure `.env` has `CHROMA_DB_DIR`, `COLLECTION_NAME`, `EMBEDDING_MODEL`

### Error: "ChromaDB query failed"
- **Fix**: Make sure you've run `ingest.py` first to populate the database

### Error: "No module named 'chromadb'"
- **Fix**: Install dependencies: `pip install chromadb sentence-transformers`

### Error: "EXTRACT_ATTRIBUTES_SYSTEM_PROMPT not found"
- **Fix**: Add the prompt to `.env` (same as used in `retriver.py`)

## Notes

1. **Filter Merging**: The RAG retriever merges:
   - Filters extracted from query via LLM (from `retriver.py` logic)
   - Filters extracted by agent's filter extractor
   - Both are converted to ChromaDB format and combined

2. **Query Rewriting**: Currently returns query as-is. Can be enhanced with LLM rewriting later (same as `retriver.py`)

3. **Brand Filters**: Multiple brands are handled by using the first brand (ChromaDB limitation). Can be enhanced with post-filtering if needed.

4. **Age Handling**: Age filters are converted to `age_min`/`age_max` format (matching `ingest.py` structure)

## Next Steps

1. Run `ingest.py` to populate ChromaDB
2. Test with `examples/rag_integration_demo.py`
3. Use `Agent(use_rag=True)` in your application

