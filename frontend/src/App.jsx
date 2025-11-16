import { useState } from 'react'
import SearchBar from './components/SearchBar'
import GraphView from './components/GraphView'
import InfoPanel from './components/InfoPanel'
import './App.css'

function App() {
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedWord, setSelectedWord] = useState('')

  const handleSearch = async (word) => {
    console.log('🔍 Starting search for:', word)
    setLoading(true)
    setError(null)
    setSelectedWord(word)

    try {
      const url = `http://localhost:8000/api/family?word=${encodeURIComponent(word)}`
      console.log('📡 Fetching:', url)
      
      const response = await fetch(url)
      console.log('📡 Response status:', response.status)
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      console.log('📦 Received data:', data)
      console.log('  - Nodes:', data.nodes?.length || 0)
      console.log('  - Edges:', data.edges?.length || 0)
      console.log('  - Synonyms:', data.synonyms?.length || 0)
      
      setGraphData(data)
      console.log('✅ Graph data set successfully')
    } catch (err) {
      console.error('❌ Search error:', err)
      setError(err.message)
      setGraphData(null)
    } finally {
      setLoading(false)
      console.log('🏁 Search completed')
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="title-word">Word</span>
            <span className="title-fam">Fam</span>
          </h1>
          <p className="app-subtitle">Explore word families through interactive graphs</p>
        </div>
      </header>

      <main className="app-main">
        <SearchBar onSearch={handleSearch} loading={loading} />

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div className="content-grid">
          <div className="graph-container">
            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Generating word family graph...</p>
              </div>
            ) : graphData ? (
              <GraphView data={graphData} />
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <h2>Start Exploring</h2>
                <p>Enter a word above to visualize its family connections</p>
              </div>
            )}
          </div>

          {graphData && !loading && (
            <InfoPanel data={graphData} selectedWord={selectedWord} />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by Wolfram Language + Python NLP</p>
      </footer>
    </div>
  )
}

export default App
