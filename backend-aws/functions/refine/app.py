"""
Lambda function for diagram refinement
"""
import json
import os
import sys

# Add common layer to path
sys.path.insert(0, '/opt/python')

from common.bedrock_client import BedrockClient


def lambda_handler(event, context):
    """
    Refine existing diagram based on user instructions
    
    Event body:
    {
        "current_mermaid": "string",
        "original_context": "string",
        "refinement_instruction": "string"
    }
    
    Returns:
    {
        "updated_mermaid": "string",
        "changes_made": [],
        "explanation": "string"
    }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        current_mermaid = body.get('current_mermaid', '')
        original_context = body.get('original_context', '')
        refinement_instruction = body.get('refinement_instruction', '')
        
        if not current_mermaid or not refinement_instruction:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required fields',
                    'message': 'current_mermaid and refinement_instruction are required'
                })
            }
        
        # Generate refinement using Bedrock
        bedrock = BedrockClient()
        
        prompt = f"""You are an expert at modifying Mermaid C4 diagrams based on user instructions.

CURRENT DIAGRAM:
```
{current_mermaid}
```

ORIGINAL CONTEXT:
{original_context}

USER'S REFINEMENT REQUEST:
"{refinement_instruction}"

Your task:
1. Understand what the user wants to change
2. Modify the Mermaid diagram accordingly
3. Maintain proper Mermaid syntax
4. Keep the diagram clean and legible

CRITICAL RULES:
- Use standard Mermaid flowchart syntax (graph LR or graph TD)
- Node IDs must be alphanumeric (no spaces, no special chars)
- NEVER use reserved words as node IDs: "system", "application", "graph", "class", "end"
- Keep labels SHORT and clear
- Maintain consistent styling with classDef
- Use icons: 👤 for users, 🔷 for systems, 📦 for external systems, 💾 for databases

Common modifications:
- REMOVE: Delete specified nodes and their connections
- ADD: Insert new nodes with appropriate connections
- EDIT LABEL: Change the text inside brackets [...]
- REPOSITION: Adjust node order (left/right in LR, top/bottom in TD)
- SIMPLIFY: Remove unnecessary details or nodes
- ENHANCE: Add more detail or connections

Format your response as JSON:
{{
  "updated_mermaid": "Complete updated Mermaid code",
  "changes_made": ["List of changes", "Another change"],
  "explanation": "Brief explanation of what was modified and why"
}}

Return ONLY the JSON, no markdown code blocks."""
        
        response_text = bedrock.invoke_claude(prompt, max_tokens=2000)
        
        # Parse JSON response
        response_data = json.loads(response_text)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"Error refining diagram: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to refine diagram',
                'message': str(e)
            })
        }
