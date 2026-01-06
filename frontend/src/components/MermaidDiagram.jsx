import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

function MermaidDiagram({ chart, zoom = 1 }) {
  const mermaidRef = useRef(null)

  // Analyze diagram complexity and return optimal configuration
  const getOptimalConfig = (diagramCode) => {
    if (!diagramCode) return getDefaultConfig()

    // Detect diagram type
    const isFlowchart = diagramCode.includes('graph LR') || diagramCode.includes('graph TD')
    const isC4 = diagramCode.includes('C4Context') || diagramCode.includes('Person(') || diagramCode.includes('System(')

    if (isFlowchart) {
      // Flowchart-specific configuration
      // Count nodes and relationships
      const nodeCount = (diagramCode.match(/\w+\[/g) || []).length
      const relationshipCount = (diagramCode.match(/-->/g) || []).length
      
      return {
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose',
        fontSize: 16,
        flowchart: {
          useMaxWidth: true,
          htmlLabels: true,
          curve: 'basis',
          nodeSpacing: 100,  // Horizontal space between nodes
          rankSpacing: 120,  // Vertical space between ranks
          padding: 40,
          diagramPadding: 20
        },
        themeVariables: {
          fontSize: '16px',
          fontFamily: 'Arial, sans-serif'
        }
      }
    }

    // C4 diagram configuration (original logic)
    const personCount = (diagramCode.match(/Person\(/g) || []).length
    const systemCount = (diagramCode.match(/System\(/g) || []).length
    const externalSystemCount = (diagramCode.match(/System_Ext\(/g) || []).length
    const relationshipCount = (diagramCode.match(/Rel\(/g) || []).length

    const totalElements = personCount + systemCount + externalSystemCount

    // Calculate average relationship label length
    const relMatches = diagramCode.match(/Rel\([^,]+,[^,]+,\s*"([^"]+)"/g) || []
    const avgLabelLength = relMatches.reduce((sum, rel) => {
      const match = rel.match(/"([^"]+)"/)
      return sum + (match ? match[1].length : 0)
    }, 0) / (relMatches.length || 1)

    // INTELLIGENT SPACING ALGORITHM
    let shapeMargin = 250
    let diagramMarginX = 200
    let diagramMarginY = 150
    let boxMargin = 80
    let messageFontSize = 14
    let boxWidth = 450
    let boxHeight = 200

    // Adjust based on number of relationships
    if (relationshipCount > 6) {
      shapeMargin += 100
      diagramMarginX += 80
      diagramMarginY += 60
    } else if (relationshipCount > 4) {
      shapeMargin += 50
      diagramMarginX += 40
      diagramMarginY += 30
    }

    // Adjust based on total elements
    if (totalElements > 6) {
      shapeMargin = 350
      diagramMarginX = 280
      diagramMarginY = 200
      boxMargin = 100
      messageFontSize = 13
      boxWidth = 480
      boxHeight = 220
    } else if (totalElements > 4) {
      shapeMargin = 300
      diagramMarginX = 240
      diagramMarginY = 180
      boxMargin = 90
      messageFontSize = 14
      boxWidth = 460
      boxHeight = 210
    } else if (totalElements > 2) {
      shapeMargin = 270
      diagramMarginX = 220
      diagramMarginY = 160
      boxMargin = 85
      messageFontSize = 14
      boxWidth = 450
      boxHeight = 200
    }

    // Adjust for long labels
    if (avgLabelLength > 25) {
      shapeMargin += 80
      messageFontSize = Math.max(12, messageFontSize - 1)
    } else if (avgLabelLength > 15) {
      shapeMargin += 40
    }

    return {
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
      fontSize: 16,
      flowchart: {
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis',
        padding: 40
      },
      c4: {
        diagramMarginX,
        diagramMarginY,
        c4ShapeMargin: shapeMargin,
        c4ShapePadding: 60,
        width: boxWidth,
        height: boxHeight,
        boxMargin,
        personFontSize: 17,
        personFontFamily: 'Arial, sans-serif',
        personFontWeight: 'bold',
        external_personFontSize: 17,
        systemFontSize: 17,
        systemFontFamily: 'Arial, sans-serif',
        systemFontWeight: 'bold',
        external_systemFontSize: 17,
        messageFontSize,
        messageFontFamily: 'Arial, sans-serif',
        wrap: true,
        wrapPadding: 15
      },
      themeVariables: {
        fontSize: '17px',
        fontFamily: 'Arial, sans-serif'
      }
    }
  }

  const getDefaultConfig = () => ({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    fontSize: 16,
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true,
      curve: 'basis',
      nodeSpacing: 100,
      rankSpacing: 120,
      padding: 40,
      diagramPadding: 20
    },
    c4: {
      diagramMarginX: 200,
      diagramMarginY: 150,
      c4ShapeMargin: 250,
      c4ShapePadding: 60,
      width: 450,
      height: 200,
      boxMargin: 80,
      personFontSize: 17,
      personFontFamily: 'Arial, sans-serif',
      personFontWeight: 'bold',
      external_personFontSize: 17,
      systemFontSize: 17,
      systemFontFamily: 'Arial, sans-serif',
      systemFontWeight: 'bold',
      external_systemFontSize: 17,
      messageFontSize: 14,
      messageFontFamily: 'Arial, sans-serif',
      wrap: true,
      wrapPadding: 15
    },
    themeVariables: {
      fontSize: '16px',
      fontFamily: 'Arial, sans-serif'
    }
  })

  useEffect(() => {
    if (chart) {
      // Reinitialize with optimal config based on diagram complexity
      const config = getOptimalConfig(chart)
      mermaid.initialize(config)
    }
  }, [chart])

  useEffect(() => {
    if (mermaidRef.current && chart) {
      // Clear previous diagram
      mermaidRef.current.innerHTML = ''

      // Create a unique ID for this diagram
      const id = `mermaid-${Date.now()}`

      // Render the diagram
      mermaid.render(id, chart).then(({ svg }) => {
        if (mermaidRef.current) {
          mermaidRef.current.innerHTML = svg
        }
      }).catch((error) => {
        console.error('Mermaid rendering error:', error)
        if (mermaidRef.current) {
          mermaidRef.current.innerHTML = `
            <div style="color: red; padding: 20px; border: 1px solid red; border-radius: 4px;">
              <strong>Error rendering diagram:</strong>
              <pre>${error.message}</pre>
              <details>
                <summary>Diagram Code</summary>
                <pre>${chart}</pre>
              </details>
            </div>
          `
        }
      })
    }
  }, [chart])

  return (
    <div style={{
      width: '100%',
      overflow: 'auto',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center'
    }}>
      <div
        ref={mermaidRef}
        style={{
          transform: `scale(${zoom})`,
          transformOrigin: 'center center',
          transition: 'transform 0.2s ease-out',
          width: '100%',
          display: 'flex',
          justifyContent: 'center'
        }}
      />
    </div>
  )
}

export default MermaidDiagram
