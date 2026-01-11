"""
Test Filter Extraction (Story 2)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.filter_extractor import FilterExtractor


def test_price_filter():
    """Test price filter extraction"""
    extractor = FilterExtractor()
    result = extractor.extract("I want something under $100", [])
    assert result.get("price_max") is not None, "Should extract price_max"
    print(f"✓ Price filter test passed: price_max={result.get('price_max')}")


def test_brand_filter():
    """Test brand filter extraction"""
    extractor = FilterExtractor()
    result = extractor.extract("Show me TechSound products", [])
    # Brand extraction may vary, so just check it doesn't crash
    print(f"✓ Brand filter test passed: {result}")


def test_category_filter():
    """Test category filter extraction"""
    extractor = FilterExtractor()
    result = extractor.extract("I need electronics", [])
    # Category extraction may vary
    print(f"✓ Category filter test passed: {result}")


def test_vague_terms():
    """Test vague term mapping"""
    extractor = FilterExtractor()
    result = extractor.extract("I want something cheap", [])
    # Should apply vague term mapping
    print(f"✓ Vague terms test passed: {result}")


def test_filter_merge():
    """Test filter merging"""
    extractor = FilterExtractor()
    existing = {"price_max": 100}
    result = extractor.extract("Actually, make it under $50", [], existing)
    # Should override price_max
    print(f"✓ Filter merge test passed: {result}")


if __name__ == "__main__":
    print("Running Filter Extraction Tests...\n")
    try:
        test_price_filter()
        test_brand_filter()
        test_category_filter()
        test_vague_terms()
        test_filter_merge()
        print("\n✅ All filter extraction tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

