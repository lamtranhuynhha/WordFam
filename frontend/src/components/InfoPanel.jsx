import './InfoPanel.css'

function InfoPanel({ data, selectedWord }) {
  const { meta, nodes, edges, metadata } = data

  return (
    <div className="info-panel">
      <div className="panel-section">
        <h2 className="panel-title">{selectedWord}</h2>
        {meta?.definition && (
          <div className="definition">
            <h3 className="section-label">Definition</h3>
            <p className="definition-text">{meta.definition}</p>
          </div>
        )}
      </div>

      <div className="panel-section">
        <h3 className="section-label">Graph Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-value">{nodes?.length || 0}</span>
            <span className="stat-label">Nodes</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{edges?.length || 0}</span>
            <span className="stat-label">Edges</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{metadata?.totalWords || 0}</span>
            <span className="stat-label">Related Words</span>
          </div>
        </div>
      </div>

      {data.synonyms && data.synonyms.length > 0 && (
        <div className="panel-section">
          <h3 className="section-label">Synonyms</h3>
          <div className="word-chips">
            {data.synonyms.slice(0, 10).map((word, idx) => (
              <span key={idx} className="word-chip synonym-chip">{word}</span>
            ))}
          </div>
        </div>
      )}

      {data.morphological && data.morphological.length > 0 && (
        <div className="panel-section">
          <h3 className="section-label">Morphological Variants</h3>
          <div className="word-chips">
            {data.morphological.slice(0, 8).map((word, idx) => (
              <span key={idx} className="word-chip morph-chip">{word}</span>
            ))}
          </div>
        </div>
      )}

      {data.semantic && data.semantic.length > 0 && (
        <div className="panel-section">
          <h3 className="section-label">Semantic Neighbors</h3>
          <div className="word-chips">
            {data.semantic.slice(0, 8).map((word, idx) => (
              <span key={idx} className="word-chip semantic-chip">{word}</span>
            ))}
          </div>
        </div>
      )}

      {metadata?.source && (
        <div className="panel-section metadata-section">
          <div className="metadata-badge">
            <span className="badge-icon">⚡</span>
            <span className="badge-text">{metadata.source}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default InfoPanel
