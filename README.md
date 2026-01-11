# Agent Logic (Brain) Proof of Concept

A standalone, modular Python agent that provides product recommendations using Groq LLMs via LangChain.

## Features

- **Intent Classification**: Classifies user queries (SEARCH, REFINE, CLARIFY, CHITCHAT)
- **Filter Extraction**: Extracts structured filters from natural language
- **Multi-Turn Context**: Maintains conversation history and accumulated filters
- **LLM Integration**: Uses Groq's free LLM models
- **Structured Output**: Returns JSON-formatted recommendations

## Tech Stack

- Python 3.10+
- LangChain (core usage only)
- Groq LLMs (FREE models)
- Pure Python modules (no databases, vector stores, or web frameworks)

## Setup

1. **Create virtual environment** (if not already created):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Groq API Key**:

   Create a `.env` file in the project root (copy from `.env.example`):

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your API key:

   ```
   GROQ_API_KEY=your-api-key-here
   ```

   Get your free API key from: https://console.groq.com/

   **Note**: The `.env` file is automatically loaded by `python-dotenv`. You can also set the environment variable directly if preferred.

## Project Structure

```
agent-logic-poc/
├── agent/
│   ├── core.py                 # Main agent orchestration
│   ├── intent_classifier.py    # Intent classification
│   ├── filter_extractor.py     # Filter extraction
│   ├── prompt_builder.py       # Prompt assembly
│   ├── llm_client.py           # LLM interaction
│   └── context_manager.py      # Multi-turn context
├── prompts/                    # Prompt templates
├── data/
│   └── mock_products.json      # Mock product catalog
├── tests/                      # Unit tests
├── examples/                   # Example scripts
├── config.py                   # Configuration
└── requirements.txt
```

## Usage

### Basic Example

```python
from agent.core import Agent

agent = Agent()
response = agent.process("I need wireless headphones under $100")

print(f"Intent: {response.intent}")
print(f"Recommendations: {len(response.recommendations)}")
for rec in response.recommendations:
    print(f"  - {rec['product_id']}: {rec['reasoning']}")
```

### Run Examples

```bash
# Single turn conversation
python examples/single_turn.py

# Multi-turn conversation
python examples/multi_turn.py

# Edge cases
python examples/edge_cases.py
```

### Run Tests

```bash
# Test intent classification
python tests/test_intent.py

# Test filter extraction
python tests/test_filters.py

# Test end-to-end
python tests/test_e2e.py
```

## Configuration

Edit `config.py` to customize:

- **Model**: Change `GROQ_MODEL` to `"llama3-70b-8192"` for better quality
- **Temperature**: Adjust `TEMPERATURE` (0.0-1.0)
- **Max Tokens**: Adjust `MAX_TOKENS`
- **Vague Terms**: Add mappings in `VAGUE_TERMS` dictionary

## How It Works

1. **Intent Classification**: Determines user intent from query and history
2. **Filter Extraction**: Extracts structured filters (price, brand, category, etc.)
3. **Context Update**: Merges filters with accumulated context
4. **Prompt Building**: Assembles complete prompt with system prompt, history, filters, and products
5. **LLM Call**: Calls Groq LLM via LangChain
6. **Response Parsing**: Validates and structures JSON response

## Constraints

- **Local POC only**: No databases, vector stores, or embeddings
- **Groq only**: Uses free Groq models exclusively
- **No web frameworks**: Pure Python modules
- **In-memory context**: No persistence

## Notes

- The agent uses mock product data from `data/mock_products.json`
- All context is maintained in memory (resets on restart)
- Product IDs in recommendations are validated against mock data
- Graceful fallbacks handle LLM errors

## License

This is a proof of concept for demonstration purposes.
