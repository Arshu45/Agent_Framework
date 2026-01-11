"""
Quick Start Script - Verify installation and basic functionality
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    print("="*60)
    print("Agent Logic POC - Quick Start")
    print("="*60)
    
    # Check API key
    import config
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"\n✓ .env file found")
    else:
        print(f"\n⚠️  .env file not found")
        print("  Create it by copying .env.example:")
        print("  cp .env.example .env")
        print("  Then edit .env and add your GROQ_API_KEY")
    
    if not config.GROQ_API_KEY:
        print("\n⚠️  WARNING: GROQ_API_KEY not set!")
        print("Please create a .env file with your API key:")
        print("  1. cp .env.example .env")
        print("  2. Edit .env and add: GROQ_API_KEY=your-api-key-here")
        print("\nGet your free API key from: https://console.groq.com/")
        print("\nContinuing with empty API key (will fail on LLM calls)...\n")
    else:
        print(f"\n✓ API Key configured (length: {len(config.GROQ_API_KEY)})")
    
    # Check imports
    print("\nChecking imports...")
    try:
        from agent.core import Agent
        print("✓ Agent imports successful")
    except Exception as e:
        print(f"✗ Import error: {e}")
        return
    
    # Check data files
    print("\nChecking data files...")
    import json
    try:
        with open(config.MOCK_PRODUCTS_FILE, 'r') as f:
            products = json.load(f)
        print(f"✓ Mock products loaded ({len(products)} products)")
    except Exception as e:
        print(f"✗ Error loading products: {e}")
        return
    
    # Check prompt files
    print("\nChecking prompt files...")
    prompt_files = [
        f"{config.PROMPTS_DIR}/system_prompt.txt",
        f"{config.PROMPTS_DIR}/intent_classification.txt",
        f"{config.PROMPTS_DIR}/filter_extraction.txt"
    ]
    for pf in prompt_files:
        if os.path.exists(pf):
            print(f"✓ {pf}")
        else:
            print(f"✗ Missing: {pf}")
            return
    
    print("\n" + "="*60)
    print("Setup verification complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Create .env file with your GROQ_API_KEY (if not done)")
    print("2. Run: python examples/single_turn.py")
    print("3. Or run: python examples/multi_turn.py")
    print("\nFor tests:")
    print("  python tests/test_intent.py")
    print("  python tests/test_filters.py")
    print("  python tests/test_e2e.py")

if __name__ == "__main__":
    main()

