"""
Test Intent Classification (Story 1)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.intent_classifier import IntentClassifier


def test_search_intent():
    """Test SEARCH intent classification"""
    classifier = IntentClassifier()
    result = classifier.classify("I need wireless headphones", [])
    assert result["intent"] == "SEARCH", f"Expected SEARCH, got {result['intent']}"
    print("✓ SEARCH intent test passed")


def test_refine_intent():
    """Test REFINE intent classification"""
    classifier = IntentClassifier()
    history = [{"user": "Find headphones", "agent": "Here are some headphones..."}]
    result = classifier.classify("but make it under $50", history)
    assert result["intent"] in ["REFINE", "SEARCH"], f"Expected REFINE/SEARCH, got {result['intent']}"
    print("✓ REFINE intent test passed")


def test_clarify_intent():
    """Test CLARIFY intent classification"""
    classifier = IntentClassifier()
    result = classifier.classify("What features does it have?", [])
    assert result["intent"] in ["CLARIFY", "SEARCH"], f"Expected CLARIFY/SEARCH, got {result['intent']}"
    print("✓ CLARIFY intent test passed")


def test_chitchat_intent():
    """Test CHITCHAT intent classification"""
    classifier = IntentClassifier()
    result = classifier.classify("Hello, how are you?", [])
    assert result["intent"] == "CHITCHAT", f"Expected CHITCHAT, got {result['intent']}"
    print("✓ CHITCHAT intent test passed")


if __name__ == "__main__":
    print("Running Intent Classification Tests...\n")
    try:
        test_search_intent()
        test_refine_intent()
        test_clarify_intent()
        test_chitchat_intent()
        print("\n✅ All intent classification tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

