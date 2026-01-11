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
    print("\nEnter your queries interactively.")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("Type 'reset' to start a new conversation.\n")
    
    # Initialize agent
    agent = Agent()
    
    turn = 0
    
    while True:
        turn += 1
        
        # Get user input
        print(f"\n{'='*60}")
        print(f"TURN {turn}")
        print(f"{'='*60}")
        query = input("\nYou: ").strip()
        
        # Check for exit commands
        if query.lower() in ['quit', 'exit', 'q', '']:
            print(f"\n{'='*60}")
            print("CONVERSATION ENDED")
            print(f"{'='*60}\n")
            break
        
        # Check for reset command
        if query.lower() == 'reset':
            agent.reset_session()
            turn = 0
            print("\n✓ Conversation reset. Starting fresh...\n")
            continue
        
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


if __name__ == "__main__":
    main()

