import { useState } from 'react'
import './App.css'
import DiagramGenerator from './components/DiagramGenerator'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>C4 Diagram Generator</h1>
        <p className="subtitle">Generate C4 Level 1 (System Context) diagrams from natural language</p>
      </header>
      <main className="App-main">
        <DiagramGenerator />
      </main>
      <footer className="App-footer">
        <p>Powered by AI and Mermaid.js</p>
      </footer>
    </div>
  )
}

export default App
