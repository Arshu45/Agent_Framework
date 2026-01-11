"""
Example: Edge Cases
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import Agent


def main():
    print("="*60)
    print("Edge Cases Example")
    print("="*60)
    
    agent = Agent()
    
    # Test cases
    test_cases = [
        ("Hello!", "Greeting/chitchat"),
        ("I want something cheap", "Vague price term"),
        ("Show me products", "Very general query"),
        ("Find me a laptop stand under $50 with aluminum", "Multiple filters"),
        ("What?", "Unclear query"),
    ]
    
    for query, description in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {description}")
        print(f"Query: {query}")
        print(f"{'='*60}\n")
        
        try:
            response = agent.process(query)
            print(f"✓ Success")
            print(f"  Intent: {response.intent}")
            print(f"  Recommendations: {len(response.recommendations)}")
            print(f"  Summary: {response.summary[:80]}...")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Edge Cases Complete")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

