class AIService {
  constructor(provider = 'anthropic') {
    this.provider = provider
    // Use environment variable for backend URL
    this.backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
    this.lastValidationReport = null
  }

  async getSuggestions(context) {
    // Get improvement suggestions from backend
    try {
      const response = await fetch(`${this.backendUrl}/api/diagrams/suggest-improvements`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_text: context,
          diagram_type: 'context'
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || error.detail?.message || error.detail || 'Failed to get suggestions')
      }

      const data = await response.json()
      return data
      
    } catch (error) {
      throw error
    }
  }

  async refineDiagram(currentMermaid, originalContext, refinementInstruction) {
    // Refine existing diagram based on user instructions
    try {
      const response = await fetch(`${this.backendUrl}/api/diagrams/refine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_mermaid: currentMermaid,
          original_context: originalContext,
          refinement_instruction: refinementInstruction
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || error.detail || 'Failed to refine diagram')
      }

      const data = await response.json()
      return data
      
    } catch (error) {
      throw error
    }
  }

  async generateC4Diagram(context) {
    // Call Python backend for validation and generation
    try {
      const response = await fetch(`${this.backendUrl}/api/diagrams/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_text: context,
          diagram_type: 'context'
        })
      })

      if (!response.ok) {
        const error = await response.json()
        
        // Handle both FastAPI format (error.detail.errors) and Lambda format (error.errors)
        const errors = error.errors || (error.detail && error.detail.errors)
        const questions = error.questions || (error.detail && error.detail.questions)
        const suggestions = error.suggestions || (error.detail && error.detail.suggestions)
        
        if (errors) {
          // Format validation errors with questions if present
          let errorMessage = errors.join('\n')
          
          if (questions && questions.length > 0) {
            errorMessage += '\n\n❓ Please provide more information:\n' + 
              questions.map((q, i) => `${i + 1}. ${q}`).join('\n')
          }
          
          if (suggestions && suggestions.length > 0) {
            errorMessage += '\n\n💡 Suggestions:\n' + suggestions.join('\n')
          }
          
          throw new Error(errorMessage)
        }
        throw new Error(error.message || error.detail || 'Failed to generate diagram')
      }

      const data = await response.json()
      
      // Store validation report
      this.lastValidationReport = {
        isValid: data.validation.is_valid,
        errors: data.validation.errors || [],
        warnings: data.validation.warnings || [],
        info: data.validation.suggestions || [],
        questions: data.validation.questions || []
      }

      return data.mermaid_code
      
    } catch (error) {
      if (error.message) {
        throw error
      }
      throw new Error('Failed to connect to backend. Make sure the Python server is running on port 8000.')
    }
  }

  getLastValidationReport() {
    return this.lastValidationReport
  }
}

export default AIService
