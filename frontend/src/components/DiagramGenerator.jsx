import { useState } from 'react'
import AIService from '../services/AIService'
import MermaidDiagram from './MermaidDiagram'
import './DiagramGenerator.css'

function DiagramGenerator() {
  const [context, setContext] = useState('')
  const [diagramCode, setDiagramCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [feedback, setFeedback] = useState('')
  const [qualityScore, setQualityScore] = useState(0)
  const [apiProvider, setApiProvider] = useState('anthropic') // 'openai' or 'anthropic'
  const [zoom, setZoom] = useState(1)
  const diagramRef = useState(null)
  const [suggestions, setSuggestions] = useState(null)
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  
  // Refinement state
  const [diagramHistory, setDiagramHistory] = useState([])
  const [currentVersion, setCurrentVersion] = useState(-1)
  const [refinementInstruction, setRefinementInstruction] = useState('')
  const [refining, setRefining] = useState(false)
  const [refinementFeedback, setRefinementFeedback] = useState('')

  const handleGenerate = async () => {
    if (!context.trim()) {
      setError('Please enter a solution context')
      return
    }

    setLoading(true)
    setError('')
    setFeedback('')
    setQualityScore(0)
    setSuggestions(null)
    setRefinementFeedback('')

    try {
      const aiService = new AIService(apiProvider)
      const mermaidCode = await aiService.generateC4Diagram(context)
      setDiagramCode(mermaidCode)
      
      // Add to history
      const newVersion = {
        version: 0,
        mermaid: mermaidCode,
        context: context,
        timestamp: new Date().toISOString(),
        description: 'Initial generation'
      }
      setDiagramHistory([newVersion])
      setCurrentVersion(0)
      
    } catch (err) {
      // Check if we should offer suggestions
      const errorMsg = err.message || ''
      
      // For "too short" or "gibberish" errors, just show the error
      // The backend already provides helpful suggestions in the error
      if (errorMsg.includes('Input too short') || 
          errorMsg.includes('gibberish') ||
          errorMsg.includes('Empty input')) {
        setError(errorMsg)
      }
      // For "Insufficient information" errors, fetch AI-generated suggestions
      else if (errorMsg.includes('Insufficient information') || 
               errorMsg.includes('provide more information') ||
               errorMsg.includes('Cannot identify')) {
        setError(errorMsg)
        handleGetSuggestions()
      } else {
        setError(errorMsg || 'Failed to generate diagram. Please check your API key configuration.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGetSuggestions = async () => {
    setLoadingSuggestions(true)
    try {
      const aiService = new AIService(apiProvider)
      const suggestionsData = await aiService.getSuggestions(context)
      setSuggestions(suggestionsData)
      setError('') // Clear error when showing suggestions
    } catch (err) {
      setError(err.message || 'Failed to generate suggestions')
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const handleSelectSuggestion = (improvedText) => {
    setContext(improvedText)
    setSuggestions(null)
    setError('')
    // Auto-generate with the improved text
    setTimeout(() => {
      const aiService = new AIService(apiProvider)
      setLoading(true)
      aiService.generateC4Diagram(improvedText)
        .then(mermaidCode => {
          setDiagramCode(mermaidCode)
          
          // Add to history
          const newVersion = {
            version: 0,
            mermaid: mermaidCode,
            context: improvedText,
            timestamp: new Date().toISOString(),
            description: 'Generated from suggestion'
          }
          setDiagramHistory([newVersion])
          setCurrentVersion(0)
          
          setLoading(false)
        })
        .catch(err => {
          setError(err.message)
          setLoading(false)
        })
    }, 100)
  }

  const handleRefine = async () => {
    if (!refinementInstruction.trim()) {
      setError('Please describe what you want to change')
      return
    }

    if (!diagramCode || diagramHistory.length === 0) {
      setError('No diagram to refine')
      return
    }

    setRefining(true)
    setError('')
    setRefinementFeedback('')

    try {
      const aiService = new AIService(apiProvider)
      const result = await aiService.refineDiagram(
        diagramCode,
        context,
        refinementInstruction
      )
      
      // Update diagram
      setDiagramCode(result.updated_mermaid)
      
      // Add to history
      const newVersion = {
        version: diagramHistory.length,
        mermaid: result.updated_mermaid,
        context: context,
        timestamp: new Date().toISOString(),
        description: refinementInstruction
      }
      setDiagramHistory([...diagramHistory, newVersion])
      setCurrentVersion(diagramHistory.length)
      
      // Show feedback
      setRefinementFeedback(`✅ ${result.explanation}\n\nChanges:\n${result.changes_made.map(c => `• ${c}`).join('\n')}`)
      setRefinementInstruction('')
      
    } catch (err) {
      setError(err.message || 'Failed to refine diagram')
    } finally {
      setRefining(false)
    }
  }

  const handleUndo = () => {
    if (currentVersion > 0) {
      const newVersion = currentVersion - 1
      setCurrentVersion(newVersion)
      setDiagramCode(diagramHistory[newVersion].mermaid)
      setRefinementFeedback(`⬅️ Undid: ${diagramHistory[currentVersion].description}`)
    }
  }

  const handleRedo = () => {
    if (currentVersion < diagramHistory.length - 1) {
      const newVersion = currentVersion + 1
      setCurrentVersion(newVersion)
      setDiagramCode(diagramHistory[newVersion].mermaid)
      setRefinementFeedback(`➡️ Redid: ${diagramHistory[newVersion].description}`)
    }
  }

  const handleClear = () => {
    setContext('')
    setDiagramCode('')
    setError('')
    setFeedback('')
    setQualityScore(0)
    setSuggestions(null)
    setDiagramHistory([])
    setCurrentVersion(-1)
    setRefinementInstruction('')
    setRefinementFeedback('')
  }

  const handleExport = () => {
    const blob = new Blob([diagramCode], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'c4-diagram.mmd'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="diagram-generator">
      <div className="input-section">
        <div className="controls-header">
          <h2>Solution Context</h2>
          <div className="api-selector">
            <label>AI Provider:</label>
            <select value={apiProvider} onChange={(e) => setApiProvider(e.target.value)}>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic (Claude)</option>
            </select>
          </div>
        </div>

        <textarea
          className="context-input"
          placeholder="Describe your system context here...&#10;&#10;Example:&#10;We are building an e-commerce platform called ShopEasy. The system will be used by customers to browse and purchase products. It needs to integrate with a payment gateway (Stripe) for processing payments, a shipping provider (FedEx API) for tracking deliveries, and an email service (SendGrid) for sending order confirmations. Internal administrators will manage the product catalog and view orders through an admin dashboard."
          value={context}
          onChange={(e) => setContext(e.target.value)}
          rows={12}
        />

        <div className="button-group">
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={loading || !context.trim()}
          >
            {loading ? 'Generating...' : 'Generate Diagram'}
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {loadingSuggestions && (
          <div className="suggestions-loading" style={{
            padding: '1rem',
            background: '#f0f7ff',
            border: '1px solid #b3d9ff',
            borderRadius: '4px',
            marginTop: '1rem'
          }}>
            <p>🤔 Analyzing your input and generating suggestions...</p>
          </div>
        )}

        {suggestions && (
          <div className="suggestions-container" style={{
            marginTop: '1rem',
            padding: '1.5rem',
            background: '#f0f7ff',
            border: '2px solid #4a90e2',
            borderRadius: '8px'
          }}>
            <h3 style={{ marginTop: 0, color: '#2c5aa0' }}>
              💡 Suggested Improvements
            </h3>
            <p style={{ marginBottom: '1rem', color: '#555' }}>
              Based on your input, here are some interpretations that would work well for C4 diagrams:
            </p>
            
            {suggestions.suggestions.map((suggestion, index) => (
              <div key={index} style={{
                marginBottom: '1rem',
                padding: '1rem',
                background: 'white',
                border: '1px solid #d0e7ff',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#4a90e2'
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(74, 144, 226, 0.2)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#d0e7ff'
                e.currentTarget.style.boxShadow = 'none'
              }}
              onClick={() => handleSelectSuggestion(suggestion.improved_text)}>
                <h4 style={{ marginTop: 0, color: '#2c5aa0' }}>
                  Option {index + 1}: {suggestion.title}
                </h4>
                <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>
                  {suggestion.description}
                </p>
                <p style={{ 
                  fontSize: '0.95rem', 
                  color: '#333',
                  padding: '0.75rem',
                  background: '#f8f9fa',
                  borderRadius: '4px',
                  borderLeft: '3px solid #4a90e2'
                }}>
                  {suggestion.improved_text}
                </p>
                <button 
                  className="btn btn-primary"
                  style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}
                  onClick={(e) => {
                    e.stopPropagation()
                    handleSelectSuggestion(suggestion.improved_text)
                  }}
                >
                  Use This Version
                </button>
              </div>
            ))}
            
            <button 
              className="btn btn-secondary"
              style={{ marginTop: '0.5rem' }}
              onClick={() => setSuggestions(null)}
            >
              Cancel - I'll Edit Manually
            </button>
          </div>
        )}

        {feedback && (
          <div className={`feedback-message ${qualityScore >= 80 ? 'excellent' : qualityScore >= 60 ? 'good' : 'acceptable'}`}>
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>
              {feedback}
            </pre>
          </div>
        )}
      </div>

      {diagramCode && (
        <div className="output-section">
          <div className="output-header">
            <h2>Generated C4 Diagram</h2>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button
                  className="btn btn-zoom"
                  onClick={() => setZoom(prev => Math.max(prev - 0.2, 0.5))}
                  title="Zoom Out"
                >
                  −
                </button>
                <span style={{
                  padding: '0.5rem 1rem',
                  background: '#f5f5f5',
                  borderRadius: '4px',
                  fontSize: '0.9rem',
                  minWidth: '60px',
                  textAlign: 'center'
                }}>
                  {Math.round(zoom * 100)}%
                </span>
                <button
                  className="btn btn-zoom"
                  onClick={() => setZoom(prev => Math.min(prev + 0.2, 3))}
                  title="Zoom In"
                >
                  +
                </button>
                <button
                  className="btn btn-zoom"
                  onClick={() => setZoom(1)}
                  title="Reset Zoom"
                  style={{ fontSize: '0.85rem' }}
                >
                  Reset
                </button>
              </div>
              <button className="btn btn-export" onClick={handleExport}>
                Export Mermaid Code
              </button>
            </div>
          </div>

          <div className="diagram-container">
            <MermaidDiagram chart={diagramCode} zoom={zoom} />
          </div>

          {/* Refinement Section */}
          <div className="refinement-section" style={{
            marginTop: '1.5rem',
            padding: '1.5rem',
            background: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #dee2e6'
          }}>
            <h3 style={{ marginTop: 0, color: '#495057' }}>
              ✨ Refine Diagram
            </h3>
            
            {diagramHistory.length > 0 && (
              <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
                Version {currentVersion + 1} of {diagramHistory.length}
                {currentVersion >= 0 && diagramHistory[currentVersion] && (
                  <span style={{ marginLeft: '1rem', fontStyle: 'italic' }}>
                    ({diagramHistory[currentVersion].description})
                  </span>
                )}
              </div>
            )}

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
              <button
                className="btn btn-secondary"
                onClick={handleUndo}
                disabled={currentVersion <= 0 || refining}
                style={{ fontSize: '0.9rem' }}
              >
                ⬅️ Undo
              </button>
              <button
                className="btn btn-secondary"
                onClick={handleRedo}
                disabled={currentVersion >= diagramHistory.length - 1 || refining}
                style={{ fontSize: '0.9rem' }}
              >
                ➡️ Redo
              </button>
            </div>

            <textarea
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '4px',
                border: '1px solid #ced4da',
                fontSize: '0.95rem',
                fontFamily: 'inherit',
                resize: 'vertical',
                minHeight: '80px'
              }}
              placeholder="Describe what you want to change...&#10;&#10;Examples:&#10;• Remove the S3 bucket&#10;• Add a database to the left of the main system&#10;• Change the user description to 'External Customers'&#10;• Simplify the diagram&#10;• Add a cache server between the system and database"
              value={refinementInstruction}
              onChange={(e) => setRefinementInstruction(e.target.value)}
              disabled={refining}
            />

            <button
              className="btn btn-primary"
              onClick={handleRefine}
              disabled={refining || !refinementInstruction.trim()}
              style={{ marginTop: '0.75rem' }}
            >
              {refining ? 'Refining...' : 'Apply Changes'}
            </button>

            {refinementFeedback && (
              <div style={{
                marginTop: '1rem',
                padding: '1rem',
                background: '#d4edda',
                border: '1px solid #c3e6cb',
                borderRadius: '4px',
                color: '#155724',
                fontSize: '0.9rem',
                whiteSpace: 'pre-wrap'
              }}>
                {refinementFeedback}
              </div>
            )}
          </div>

          <details className="code-details">
            <summary>View Mermaid Code</summary>
            <pre className="code-block">
              <code>{diagramCode}</code>
            </pre>
          </details>
        </div>
      )}
    </div>
  )
}

export default DiagramGenerator
