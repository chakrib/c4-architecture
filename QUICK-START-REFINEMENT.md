# Quick Start - Diagram Refinement

## Try It Now!

### 1. Generate a Diagram

Start the servers and generate any diagram:
```
Input: "Build a web app where users upload files to S3 and transfer to SFTP servers"
```

### 2. See the Refinement Section

Below the diagram, you'll see:
```
✨ Refine Diagram
Version 1 of 1 (Initial generation)
[⬅️ Undo] [➡️ Redo]
```

### 3. Try These Refinements

#### Remove an Element
```
"Remove the S3 bucket"
```
**Result**: S3 node and its connections disappear

#### Add an Element
```
"Add a database to the left of the main system"
```
**Result**: Database node appears on the left

#### Change a Label
```
"Change the user description to 'External Customers'"
```
**Result**: User node label updates

#### Simplify
```
"Make it simpler"
```
**Result**: Diagram becomes more concise

### 4. Use Undo/Redo

- Click **⬅️ Undo** to go back
- Click **➡️ Redo** to go forward
- See version number update

### 5. See Feedback

After each change:
```
✅ Removed S3Bucket node

Changes:
• Removed S3Bucket node
• Removed connection from MainSystem to S3Bucket
```

## Example Session

### Step 1: Initial Diagram
```
Input: "Build a web app where users upload files to S3, process them, 
        and store results in a database"

Generated:
User → WebApp → S3
       ↓
    Database
```

### Step 2: Remove S3
```
Refinement: "Remove the S3 bucket"

Result:
User → WebApp → Database

Feedback: ✅ Removed S3Bucket node and connections
Version: 2 of 2
```

### Step 3: Add Cache
```
Refinement: "Add a cache between the web app and database"

Result:
User → WebApp → Cache → Database

Feedback: ✅ Added Cache node between WebApp and Database
Version: 3 of 3
```

### Step 4: Undo
```
Action: Click ⬅️ Undo

Result: Back to version 2 (no cache)

Feedback: ⬅️ Undid: Add a cache between the web app and database
Version: 2 of 3
```

### Step 5: Different Change
```
Refinement: "Change user to 'Mobile App Users'"

Result:
Mobile App Users → WebApp → Database

Feedback: ✅ Updated User node label
Version: 3 of 3 (replaces previous version 3)
```

## Common Refinement Patterns

### Removing Elements
```
✅ "Remove the database"
✅ "Delete the S3 bucket"
✅ "Remove the connection between X and Y"
```

### Adding Elements
```
✅ "Add a cache server"
✅ "Add a database to the left of the system"
✅ "Insert an API gateway between user and system"
```

### Changing Labels
```
✅ "Change user to 'Customers'"
✅ "Rename System to 'Payment Service'"
✅ "Update the description of the main system"
```

### Repositioning
```
✅ "Move database to the left"
✅ "Put cache above the system"
✅ "Swap X and Y positions"
```

### Simplifying
```
✅ "Make it simpler"
✅ "Remove unnecessary details"
✅ "Simplify the connections"
```

### Enhancing
```
✅ "Add more detail"
✅ "Show data flow more clearly"
✅ "Add descriptions to connections"
```

## Tips

1. **Be Specific** - "Remove the S3 bucket" is better than "remove something"
2. **One Change at a Time** - Easier to undo if needed
3. **Use Undo Freely** - Experiment without fear
4. **Check Feedback** - Understand what changed
5. **Iterate** - Multiple small changes work better than one big change

## Troubleshooting

### Refinement doesn't work as expected
- Try being more specific in your instruction
- Check the feedback to see what actually changed
- Use undo and try a different instruction

### Undo/Redo buttons disabled
- Undo disabled: You're at the first version
- Redo disabled: You're at the latest version
- Both disabled: Refinement in progress

### Lost history after refresh
- Current version uses client-side state only
- History is lost on page refresh
- This is expected behavior (will be improved later)

## What's Next?

After trying refinement:
1. ✅ Experiment with different types of changes
2. ✅ Try complex multi-step refinements
3. ✅ Use undo/redo to explore alternatives
4. ✅ See how the AI interprets your instructions

## Status

🟢 **READY TO USE** - Diagram refinement is fully functional!

Start refining your diagrams now! 🎨
