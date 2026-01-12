"""
Demo: Agent with RAG Retriever Integration
Shows how the agent works with ChromaDB vector search
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import Agent


def main():
    print("="*60)
    print("Agent with RAG Retriever (ChromaDB) Demo")
    print("="*60)
    print("\nThis demo shows the agent:")
    print("1. Using ChromaDB vector search (RAG)")
    print("2. Processing user queries with semantic search")
    print("3. Generating recommendations from vector DB results\n")
    
    try:
        # Initialize agent with RAG
        agent = Agent(use_rag=True)
        
        # Example query
        query = input("Enter your search query: ").strip()
        if not query:
            query = "I need electronics"
        
        print(f"\nQuery: {query}\n")
        
        # Process query
        response = agent.process(query)
        
        # Display results
        print("\n" + "="*60)
        print("AGENT RESPONSE")
        print("="*60)
        print(f"\nIntent: {response.intent}")
        print(f"\nFilters Applied:")
        for key, value in response.filters.items():
            if value:
                print(f"  - {key}: {value}")
        
        print(f"\nRecommendations ({len(response.recommendations)}):")
        for i, rec in enumerate(response.recommendations, 1):
            print(f"\n  {i}. {rec.get('product_name', 'Unknown')} (ID: {rec['product_id']})")
            print(f"     Reasoning: {rec['reasoning'][:80]}...")
        
        print(f"\nSummary: {response.summary}")
        
        if response.follow_up_questions:
            print(f"\nFollow-up Questions:")
            for i, question in enumerate(response.follow_up_questions, 1):
                print(f"  {i}. {question}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. ChromaDB is set up (run ingest.py first)")
        print("2. .env file has CHROMA_DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL")
        print("3. EXTRACT_ATTRIBUTES_SYSTEM_PROMPT is set in .env")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

