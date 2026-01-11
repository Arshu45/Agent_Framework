"""
Example: Single Turn Conversation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import Agent


def main():
    print("="*60)
    print("Single Turn Example")
    print("="*60)
    
    # Initialize agent
    agent = Agent()
    
    # Single query
    # query = "I need wireless headphones under $100"
    query = input("Enter your query: ")
    print(f"\nUser Query: {query}\n")
    
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
        print(f"\n  {i}. Product ID: {rec['product_id']}")
        print(f"     Product Name: {rec['product_name']}")
        print(f"     Reasoning: {rec['reasoning']}")
    
    print(f"\nSummary: {response.summary}")
    
    if response.follow_up_questions:
        print(f"\nFollow-up Questions ({len(response.follow_up_questions)}):")
        for i, question in enumerate(response.follow_up_questions, 1):
            print(f"  {i}. {question}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

