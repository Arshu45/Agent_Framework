"""
Example: Multi-Turn Conversation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import Agent


def main():
    print("="*60)
    print("Multi-Turn Conversation Example")
    print("="*60)
    
    # Initialize agent
    agent = Agent()
    
    # Conversation flow
    queries = [
        "I'm looking for electronics",
        "Actually, I need headphones specifically",
        "Make it wireless and under $80",
        "What features do they have?"
    ]
    
    for turn, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"TURN {turn}")
        print(f"{'='*60}")
        print(f"\nUser: {query}\n")
        
        # Process query
        response = agent.process(query)
        
        # Display results
        print(f"\nAgent Intent: {response.intent}")
        print(f"\nCurrent Filters:")
        filters_display = {k: v for k, v in response.filters.items() if v}
        if filters_display:
            for key, value in filters_display.items():
                print(f"  - {key}: {value}")
        else:
            print("  (no filters)")
        
        print(f"\nRecommendations ({len(response.recommendations)}):")
        for i, rec in enumerate(response.recommendations[:3], 1):  # Show first 3
            product_name = rec.get('product_name', 'Unknown Product')
            print(f"  {i}. {rec['product_id']} - {product_name}")
            print(f"     Reasoning: {rec['reasoning']}")
        
        print(f"\nSummary: {response.summary}")
        
        if response.follow_up_questions:
            print(f"\nFollow-up Questions:")
            for i, question in enumerate(response.follow_up_questions, 1):
                print(f"  {i}. {question}")
    
    print(f"\n{'='*60}")
    print("CONVERSATION COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

