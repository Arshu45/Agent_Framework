"""
Demo: Agent with API Product Retriever
Shows how the agent retrieves products from free API and processes queries
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import Agent


def main():
    print("="*60)
    print("Agent with API Product Retriever Demo")
    print("="*60)
    print("\nThis demo shows the agent:")
    print("1. Retrieving products from free API (FakeStore)")
    print("2. Processing user queries with retrieved products")
    print("3. Generating recommendations\n")
    
    # Initialize agent (uses ProductRetriever by default)
    agent = Agent()
    
    # Example queries
    queries = [
        "I need some clothes",
        "Show me clothes under $50"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"QUERY {i}: {query}")
        print(f"{'='*60}\n")
        
        try:
            response = agent.process(query)
            
            print(f"\n✓ Intent: {response.intent}")
            print(f"✓ Filters: {response.filters}")
            print(f"✓ Recommendations: {len(response.recommendations)}")
            
            for j, rec in enumerate(response.recommendations[:3], 1):
                print(f"\n  {j}. {rec.get('product_name', 'Unknown')} (ID: {rec['product_id']})")
                print(f"     {rec['reasoning'][:80]}...")
            
            if response.follow_up_questions:
                print(f"\n✓ Follow-up Questions:")
                for q in response.follow_up_questions[:2]:
                    print(f"  - {q}")
                    
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Demo Complete!")
    print(f"{'='*60}\n")
    print("Note: Products are retrieved from FakeStore API")
    print("In production, this would be replaced with your RAG retriever.")


if __name__ == "__main__":
    main()

