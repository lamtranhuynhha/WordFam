# WordFam Frontend

Beautiful React frontend for exploring word family graphs.

## 🎨 Design

Built with custom color palette:
- Primary: `#ae121b`, `#e91823`, `#700915`
- Accent: `#f176ae`, `#f4bcce`
- Background: `#35181c`

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 📦 Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **Cytoscape.js** - Graph visualization
- **Axios** - HTTP client

## 🔧 Configuration

The frontend expects the backend API at `http://localhost:8000`.

To change this, update the proxy in `vite.config.js` or modify the fetch URL in `App.jsx`.

## 🎯 Features

- ✅ Interactive word family graph visualization
- ✅ Real-time search with example words
- ✅ Beautiful gradient UI with custom color palette
- ✅ Responsive design
- ✅ Node hover effects and animations
- ✅ Info panel with word metadata
- ✅ Graph statistics and relationship types

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SearchBar.jsx      # Search input with examples
│   │   ├── GraphView.jsx      # Cytoscape graph visualization
│   │   └── InfoPanel.jsx      # Word metadata sidebar
│   ├── App.jsx                # Main app component
│   ├── App.css                # App styles
│   ├── index.css              # Global styles
│   └── main.jsx               # Entry point
├── index.html
├── vite.config.js
└── package.json
```

## 🎨 Graph Legend

- **Red (#e91823)**: Root word / Synonyms
- **Pink (#f176ae)**: Morphological variants
- **Light Pink (#f4bcce)**: Semantic neighbors

## 🔗 API Integration

The frontend calls:
```
GET http://localhost:8000/api/family?word={word}
```

Expected response format:
```json
{
  "nodes": [...],
  "edges": [...],
  "meta": { "definition": "..." },
  "synonyms": [...],
  "morphological": [...],
  "semantic": [...],
  "metadata": { "source": "..." }
}
```
