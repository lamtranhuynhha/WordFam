import { useState } from 'react'
import './SearchBar.css'

function SearchBar({ onSearch, loading }) {
  const [inputValue, setInputValue] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const word = inputValue.trim()
    if (word && !loading) {
      onSearch(word)
    }
  }

  const handleExampleClick = (word) => {
    setInputValue(word)
    onSearch(word)
  }

  const examples = ['run', 'act', 'create', 'think', 'happy']

  return (
    <div className="search-bar-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-wrapper">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter a word to explore..."
            className="search-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={loading || !inputValue.trim()}
          >
            {loading ? '⏳' : '🔍'}
          </button>
        </div>
      </form>

      <div className="examples">
        <span className="examples-label">Try:</span>
        {examples.map((word) => (
          <button
            key={word}
            onClick={() => handleExampleClick(word)}
            className="example-chip"
            disabled={loading}
          >
            {word}
          </button>
        ))}
      </div>
    </div>
  )
}

export default SearchBar
