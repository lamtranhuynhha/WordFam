# WordFam 🔤

**Explore word families through interactive visual graphs**

WordFam is a web application that generates and visualizes morphological word families, helping users understand relationships between words through etymology, derivations, and semantic connections.

![WordFam Demo](https://img.shields.io/badge/status-hackathon-blue)

## ✨ Features

- **Interactive Graph Visualization** - Explore word relationships with Cytoscape.js
- **Multiple Data Sources** - Combines WordNet, Datamuse API, morphological analysis, and embeddings
- **Smart Word Validation** - Ensures only real words appear in graphs
- **Etymology-Based Filtering** - Distinguishes true derivations from false cognates
- **Compound Word Detection** - Recognizes phrasal verbs and compound words
- **Word Definitions** - Click any node to see its definition
- **Fast Performance** - Parallel API calls for sub-5-second response times

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## 📁 Project Structure

```
WordFam/
├── backend/
│   ├── models/          # Pydantic response models
│   ├── services/        # Core engines (WordNet, Datamuse, morphology, etc.)
│   ├── utils/           # Caching utilities
│   └── app.py           # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/  # React components (GraphView, SearchBar, InfoPanel)
│   │   ├── App.jsx      # Main app
│   │   └── index.css    # Global styles
│   └── package.json
└── README.md
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI - High-performance async web framework
- NLTK WordNet - Lexical database for derivations
- Datamuse API - Word associations and validations
- Sentence Transformers - Semantic similarity embeddings
- Free Dictionary API - Word definitions

**Frontend:**
- React - UI framework
- Cytoscape.js - Graph visualization
- Axios - HTTP client
- Vite - Build tool

## 🎯 How It Works

1. **Input**: User enters a word (e.g., "happy")
2. **Processing**: Backend queries multiple sources in parallel:
   - WordNet for derivations
   - Datamuse for related words
   - Morphology engine for variants
   - Compound words database
   - Etymology validation
3. **Validation**: All words verified to exist in dictionaries
4. **Graph Building**: Nodes (words) and edges (relationships) constructed
5. **Visualization**: Interactive graph rendered with color-coded relationships

## 🎨 Graph Legend

- 🔴 **Red** - Root word / High relevance
- 🩷 **Pink** - Morphological derivations
- 💗 **Light Pink** - Semantic relations

## 📝 API Endpoints

### `GET /api/family?word={word}`

Returns word family graph data:

```json
{
  "nodes": [{"id": "happy", "label": "happy", "score": 1.0, "definition": "..."}],
  "edges": [{"source": "happy", "target": "happiness", "type": "morphological"}],
  "synonyms": ["joyful", "glad"],
  "semantic": ["pleased", "content"],
  "meta": {"definition": "...", "etymology": "..."}
}
```

## 🧪 Example Queries

- **run** → runner, running, runway, runaway, rerun, overrun

## 👥 Team

Developed during CS Girlies Hackathon 2025

## 📄 License

MIT License
