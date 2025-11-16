# WordFam Backend

FastAPI backend for generating word family graphs using NLP techniques.

## Features

- **WordNet Integration**: Synonyms, derivations, hypernyms, and hyponyms
- **Semantic Embeddings**: Using SentenceTransformer (MiniLM) for similarity
- **Morphological Analysis**: Prefix/suffix detection and variant generation.
- **Wolfram API**: Optional integration for definitions and etymology
- **Caching**: In-memory caching for improved performance

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` to set your Wolfram API URL

### 3. Run the Server

```bash
# Development
python app.py

# Or with uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### `GET /api/family?word={word}`

Generate a word family graph for the given word.

**Parameters:**
- `word` (required): The root word to analyze

**Response:**
```json
{
  "nodes": [
    {"id": "run", "label": "run", "score": 1.0},
    {"id": "running", "label": "running", "score": 0.85}
  ],
  "edges": [
    {"source": "run", "target": "running", "type": "derivation"}
  ],
  "meta": {
    "definition": "...",
    "etymology": "...",
    "usage": "..."
  }
}
```

## Architecture

```
backend/
├── app.py                 # FastAPI application
├── services/              # Core business logic
│   ├── wordnet_engine.py  # WordNet integration
│   ├── embedding_engine.py # Embedding similarity
│   ├── morph_engine.py    # Morphological analysis
│   ├── wolfram_service.py # Wolfram API client
│   └── graph_builder.py   # Graph construction
├── models/
│   └── response.py        # Pydantic models
└── utils/
    └── cache.py          # Caching utilities
```

## Deployment

### Render

1. Create a new Web Service on Render
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables if needed


