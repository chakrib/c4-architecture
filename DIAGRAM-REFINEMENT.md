# Diagram Refinement Feature

## Overview

The C4 diagram generator now supports **interactive diagram refinement** - users can modify generated diagrams using natural language commands with full undo/redo support.

## Features

### 1. Natural Language Modifications ✨
Users can describe changes in plain English:
- "Remove the S3 bucket"
- "Add a database to the left of the main system"
- "Change the user description to 'External Customers'"
- "Simplify the diagram"
- "Add a cache server between the system and database"

### 2. Version History 📚
- Every change creates a new version
- Full history tracked in client-side state
- See current version number (e.g., "Version 2 of 5")
- Each version includes description of what changed

### 3. Undo/Redo ⬅️➡️
- Undo button: Go back to previous version
- Redo button: Move forward to next version
- Buttons disabled when at start/end of history
- Visual feedback showing what was undone/redone

### 4. Change Feedback ✅
After each refinement, system shows:
- Explanation of what was modified
- List of specific changes made
- Success message with details

## User Flow

```
1. Generate initial diagram
   ↓
2. See diagram displayed
   ↓
3. Enter refinement instruction
   "Remove the S3 bucket"
   ↓
4. Click "Apply Changes"
   ↓
5. System refines diagram using Claude
   ↓
6. Updated diagram displayed
   ↓
7. Feedback shown: "✅ Removed S3Bucket node and connections"
   ↓
8. Can undo, redo, or make more changes
```

## UI Components

### Refinement Section

```
┌─────────────────────────────────────────────────────────┐
│ ✨ Refine Diagram                                       │
│                                                          │
│ Version 2 of 3 (Removed S3 bucket)                     │
│                                                          │
│ [⬅️ Undo] [➡️ Redo]                                     │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Describe what you want to change...                │ │
│ │                                                     │ │
│ │ Examples:                                           │ │
│ │ • Remove the S3 bucket                             │ │
│ │ • Add a database to the left                       │ │
│ │ • Change user description to 'Customers'           │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ [Apply Changes]                                         │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ✅ Removed S3Bucket node                            │ │
│ │                                                     │ │
│ │ Changes:                                            │ │
│ │ • Removed S3Bucket node                            │ │
│ │ • Removed connection from MainSystem to S3Bucket   │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Supported Operations

### Remove Elements
```
"Remove the database"
"Delete the S3 bucket"
"Remove the connection between user and system"
```

### Add Elements
```
"Add a cache server"
"Add a database to the left of the main system"
"Add a connection from user to database"
"Insert an API gateway between user and system"
```

### Modify Labels
```
"Change user description to 'External Customers'"
"Rename 'System' to 'Payment Service'"
"Update the main system label to include 'v2.0'"
```

### Reposition
```
"Move database to the left of the system"
"Put cache above the main system"
"Swap the positions of S3 and database"
```

### Simplify
```
"Make it simpler"
"Remove unnecessary details"
"Simplify the connections"
```

### Enhance
```
"Add more detail to the main system"
"Show the data flow more clearly"
"Add descriptions to all connections"
```

## Technical Implementation

### Backend

**New Endpoint:**
```python
POST /api/diagrams/refine
{
  "current_mermaid": "graph LR...",
  "original_context": "Build a web app...",
  "refinement_instruction": "Remove the S3 bucket"
}
```

**Response:**
```json
{
  "updated_mermaid": "graph LR...",
  "changes_made": [
    "Removed S3Bucket node",
    "Removed connection from MainSystem to S3Bucket"
  ],
  "explanation": "I removed the S3 bucket as requested and cleaned up the orphaned connections."
}
```

**Function:**
```python
def refine_diagram(current_mermaid, original_context, refinement_instruction)
    # Uses Claude to understand instruction
    # Modifies Mermaid code accordingly
    # Returns updated diagram with explanation
```

### Frontend

**State Management:**
```javascript
const [diagramHistory, setDiagramHistory] = useState([])
const [currentVersion, setCurrentVersion] = useState(-1)

// History structure:
[
  {
    version: 0,
    mermaid: "graph LR...",
    context: "Build a web app...",
    timestamp: "2024-01-01T10:00:00Z",
    description: "Initial generation"
  },
  {
    version: 1,
    mermaid: "graph LR...",
    context: "Build a web app...",
    timestamp: "2024-01-01T10:01:00Z",
    description: "Removed S3 bucket"
  }
]
```

**Handlers:**
```javascript
handleRefine()      // Apply refinement instruction
handleUndo()        // Go to previous version
handleRedo()        // Go to next version
```

**AIService Method:**
```javascript
async refineDiagram(currentMermaid, originalContext, refinementInstruction)
    // Calls backend /api/diagrams/refine
    // Returns updated diagram with changes
```

## Example Session

### Initial Generation
```
User: "Build a web app where users upload files to S3 and transfer to SFTP"
System: [Generates diagram with User, WebApp, S3, SFTP]
```

### Refinement 1: Remove Element
```
User: "Remove the S3 bucket"
System: ✅ Removed S3Bucket node and connections
        Version 2 of 2
```

### Refinement 2: Add Element
```
User: "Add a database to the left of the web app"
System: ✅ Added Database node to the left of WebApp
        Version 3 of 3
```

### Undo
```
User: [Clicks Undo]
System: ⬅️ Undid: Add a database to the left of the web app
        Version 2 of 3
```

### Refinement 3: Modify Label
```
User: "Change user description to 'External Customers'"
System: ✅ Updated User node label to 'External Customers'
        Version 3 of 3 (overwrites previous version 3)
```

## State Management

### Client-Side Only (Current)
- Stored in React component state
- Lost on page refresh
- Fast and simple
- No backend storage needed

### Version History Structure
```javascript
{
  version: number,           // Sequential version number
  mermaid: string,          // Mermaid diagram code
  context: string,          // Original context description
  timestamp: string,        // ISO timestamp
  description: string       // What changed in this version
}
```

### History Operations
- **Add**: Append new version, increment currentVersion
- **Undo**: Decrement currentVersion, load that version's mermaid
- **Redo**: Increment currentVersion, load that version's mermaid
- **Clear**: Reset history array and currentVersion to -1

## Benefits

1. **Iterative Refinement** - Perfect diagrams through multiple iterations
2. **No Manual Editing** - Natural language instead of Mermaid syntax
3. **Safe Experimentation** - Undo any change instantly
4. **Learning Tool** - See how changes affect the diagram
5. **Flexible** - Handles any type of modification

## Limitations (Current)

1. **Session Only** - History lost on page refresh
2. **No Sharing** - Can't share refinement history
3. **No Collaboration** - Single user only
4. **Memory Limit** - Browser memory constraints

## Future Enhancements

1. **LocalStorage Persistence** - Save history across refreshes
2. **Database Storage** - Full persistence and sharing
3. **Quick Actions** - Buttons for common operations
4. **Visual Editor** - Click to select and modify elements
5. **Branching** - Create alternative versions
6. **Export History** - Save refinement session
7. **Collaboration** - Multi-user refinement

## Testing

### Manual Test

1. Start servers
2. Generate a diagram
3. Try refinements:
   - "Remove the database"
   - "Add a cache server"
   - "Change user to 'Customers'"
4. Test undo/redo
5. Verify feedback messages

### API Test

```bash
curl -X POST http://localhost:8000/api/diagrams/refine \
  -H "Content-Type: application/json" \
  -d '{
    "current_mermaid": "graph LR\n  User[User]\n  System[System]\n  User-->System",
    "original_context": "Build a web app...",
    "refinement_instruction": "Add a database to the right of the system"
  }' | jq
```

## Status

🟢 **COMPLETE** - Diagram refinement feature is fully implemented with:
- ✅ Natural language modifications
- ✅ Version history tracking
- ✅ Undo/redo functionality
- ✅ Change feedback
- ✅ Client-side state management

Ready to use!
