"""
End-to-End Agent Tests
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import Agent


def test_single_turn():
    """Test single turn conversation"""
    agent = Agent()
    response = agent.process("I need wireless headphones under $100")
    
    assert response.recommendations is not None, "Should return recommendations"
    assert len(response.recommendations) > 0, "Should have at least one recommendation"
    assert response.intent in ["SEARCH", "REFINE"], "Should classify intent"
    
    print(f"✓ Single turn test passed")
    print(f"  Intent: {response.intent}")
    print(f"  Recommendations: {len(response.recommendations)}")
    print(f"  Summary: {response.summary[:50]}...")


def test_multi_turn():
    """Test multi-turn conversation"""
    agent = Agent()
    
    # Turn 1
    response1 = agent.process("Show me electronics")
    print(f"\nTurn 1 - Intent: {response1.intent}")
    
    # Turn 2 - Refinement
    response2 = agent.process("But make it under $50")
    print(f"Turn 2 - Intent: {response2.intent}")
    print(f"  Filters: {response2.filters}")
    
    assert response2.intent in ["REFINE", "SEARCH"], "Should recognize refinement"
    
    print(f"\n✓ Multi-turn test passed")


def test_context_persistence():
    """Test context persistence across turns"""
    agent = Agent()
    
    agent.process("I want headphones")
    agent.process("Actually, make it wireless")
    
    filters = agent.context_manager.get_filters()
    history = agent.context_manager.get_history()
    
    assert len(history) == 2, "Should have 2 turns in history"
    print(f"✓ Context persistence test passed")
    print(f"  History length: {len(history)}")
    print(f"  Filters: {filters}")


if __name__ == "__main__":
    print("Running End-to-End Tests...\n")
    try:
        test_single_turn()
        print()
        test_multi_turn()
        print()
        test_context_persistence()
        print("\n✅ All E2E tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

