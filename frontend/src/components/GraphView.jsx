import { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import './GraphView.css'

function GraphView({ data }) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    console.log('🎨 GraphView useEffect triggered', { 
      hasData: !!data, 
      hasContainer: !!containerRef.current,
      nodeCount: data?.nodes?.length,
      edgeCount: data?.edges?.length 
    })

    if (!data) {
      console.warn('⚠️ GraphView: No data provided')
      return
    }

    if (!containerRef.current) {
      console.warn('⚠️ GraphView: Container ref not attached')
      return
    }

    if (!data.nodes || data.nodes.length === 0) {
      console.warn('⚠️ GraphView: No nodes in data')
      return
    }

    console.log('✅ GraphView: Starting Cytoscape initialization...')

    // Transform data to Cytoscape format
    const elements = [
      ...data.nodes.map(node => ({
        data: {
          id: node.id,
          label: node.label,
          score: node.score,
          definition: node.definition
        }
      })),
      ...data.edges.map(edge => ({
        data: {
          id: `${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target,
          type: edge.type
        }
      }))
    ]

    console.log('📊 Cytoscape elements prepared:', {
      totalElements: elements.length,
      nodes: elements.filter(e => !e.data.source).length,
      edges: elements.filter(e => e.data.source).length
    })

    // Initialize Cytoscape
    try {
      console.log('🚀 Creating Cytoscape instance...')
      cyRef.current = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele) => {
              const score = ele.data('score')
              if (score >= 0.95) return '#e91823'
              if (score >= 0.85) return '#f176ae'
              if (score >= 0.80) return '#f4bcce'
              return '#ae121b'
            },
            'label': 'data(label)',
            'color': '#ffffff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '14px',
            'font-weight': 'bold',
            'text-outline-width': 2,
            'text-outline-color': '#35181c',
            'width': (ele) => {
              const score = ele.data('score')
              return score >= 0.95 ? 60 : 45
            },
            'height': (ele) => {
              const score = ele.data('score')
              return score >= 0.95 ? 60 : 45
            },
            'border-width': 3,
            'border-color': '#700915',
            'transition-property': 'background-color, border-color',
            'transition-duration': '0.3s'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#f176ae',
            'border-width': 4
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': (ele) => {
              const type = ele.data('type')
              if (type === 'synonym') return '#e91823'
              if (type === 'morphological') return '#f176ae'
              if (type === 'semantic') return '#f4bcce'
              return '#ae121b'
            },
            'target-arrow-color': (ele) => {
              const type = ele.data('type')
              if (type === 'synonym') return '#e91823'
              if (type === 'morphological') return '#f176ae'
              if (type === 'semantic') return '#f4bcce'
              return '#ae121b'
            },
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': 0.7
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 1000,
        nodeRepulsion: 8000,
        idealEdgeLength: 100,
        edgeElasticity: 100,
        nestingFactor: 1.2,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0
      },
      minZoom: 0.5,
      maxZoom: 3
    })

    console.log('✅ Cytoscape instance created successfully!')
    console.log('📍 Graph has', cyRef.current.nodes().length, 'nodes and', cyRef.current.edges().length, 'edges')

    // Add hover effects
    cyRef.current.on('mouseover', 'node', function(evt) {
      const node = evt.target
      node.style('background-color', '#f8bbd7')
    })

    cyRef.current.on('mouseout', 'node', function(evt) {
      const node = evt.target
      const score = node.data('score')
      if (score >= 0.95) node.style('background-color', '#e91823')
      else if (score >= 0.85) node.style('background-color', '#f176ae')
      else if (score >= 0.80) node.style('background-color', '#f4bcce')
      else node.style('background-color', '#ae121b')
    })

    // Add click event to show definition
    cyRef.current.on('tap', 'node', function(evt) {
      const node = evt.target
      const nodeData = node.data()
      const position = node.renderedPosition()
      
      console.log('Node clicked:', nodeData)
      
      if (nodeData.definition) {
        setSelectedNode({
          label: nodeData.label,
          definition: nodeData.definition,
          score: nodeData.score
        })
        setTooltipPos({ 
          x: position.x, 
          y: position.y - 50 
        })
      }
    })

    // Click on background to close tooltip
    cyRef.current.on('tap', function(evt) {
      if (evt.target === cyRef.current) {
        setSelectedNode(null)
      }
    })

    } catch (error) {
      console.error('❌ Error creating Cytoscape instance:', error)
      console.error('Error details:', error.message, error.stack)
    }

    return () => {
      if (cyRef.current) {
        console.log('🧹 Cleaning up Cytoscape instance')
        cyRef.current.destroy()
      }
    }
  }, [data])

  return (
    <div className="graph-view">
      <div 
        ref={containerRef} 
        className="cytoscape-container"
        style={{ border: '2px solid rgba(241, 118, 174, 0.3)' }}
      />
      <div className="graph-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ background: '#e91823' }}></span>
          <span>Root/Synonym</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ background: '#f176ae' }}></span>
          <span>Morphological</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ background: '#f4bcce' }}></span>
          <span>Semantic</span>
        </div>
      </div>

      {selectedNode && (
        <div 
          className="node-tooltip"
          style={{
            position: 'absolute',
            left: `${tooltipPos.x}px`,
            top: `${tooltipPos.y}px`,
            transform: 'translate(-50%, -100%)'
          }}
        >
          <button 
            className="tooltip-close"
            onClick={() => setSelectedNode(null)}
          >
            ×
          </button>
          <h4 className="tooltip-word">{selectedNode.label}</h4>
          <p className="tooltip-definition">{selectedNode.definition}</p>
        </div>
      )}
    </div>
  )
}

export default GraphView
