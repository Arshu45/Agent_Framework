# RAG Integration Notes

## How RAG Retriever Works vs Current Implementation

### With RAG (Production):

```
User Query → RAG Retriever
  ↓
1. Embed query (semantic search)
2. Vector similarity search in Vector DB
3. Apply metadata filters (price, category, etc.) in query
4. Return: Semantically matched + filtered products
  ↓
Agent receives pre-filtered products
  ↓
Agent processes with LLM
```

**RAG does:**

- ✅ Semantic search (vector similarity)
- ✅ Metadata filtering (in vector DB query)
- ✅ Returns relevant products

**Agent does:**

- ✅ Intent classification
- ✅ Filter extraction (for context)
- ✅ Prompt building
- ✅ LLM recommendation generation
- ⚠️ Optional post-filtering (usually not needed if RAG did it right)

### Current API Retriever (Testing Only):

```
User Query → API Retriever
  ↓
1. Fetch all products from API
2. Simple keyword matching (TEMPORARY - only because API has no semantic search)
3. Apply metadata filters
4. Return: Keyword-matched + filtered products
```

**Why keyword matching?**

- The free FakeStore API doesn't support semantic search
- This is a temporary workaround for testing
- When RAG is plugged in, RAG handles semantic search

## Key Point

**RAG already does semantic search**, so:

- ✅ RAG retriever: Returns semantically matched products
- ❌ Agent: Should NOT duplicate semantic matching
- ✅ Agent: Can optionally post-filter (but usually not needed)

## Integration Checklist

When integrating your RAG retriever:

1. **RAG Retriever Interface:**

   ```python
   def retrieve(query: str, filters: Dict, top_k: int) -> List[Dict]:
       # Your RAG does:
       # 1. Semantic search (vector similarity)
       # 2. Metadata filtering (in vector DB)
       # 3. Returns filtered products
       pass
   ```

2. **Agent Usage:**

   ```python
   from agent.core import Agent
   from your_rag import YourRAGRetriever

   rag = YourRAGRetriever()
   agent = Agent(product_retriever=rag)
   ```

3. **What Agent Expects:**

   - Products already semantically matched by RAG
   - Products already filtered by metadata (if RAG supports it)
   - Products in standard format: `{id, name, category, brand, price, rating, features}`

4. **Optional Post-Filtering:**
   - Agent can do additional filtering if needed
   - But usually RAG results are sufficient

## Summary

- **RAG = Semantic Search + Metadata Filtering**
- **Agent = Intent + Filter Extraction + Prompt Building + LLM**
- **No duplication** - each component has its role
