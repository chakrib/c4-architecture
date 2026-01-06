"""
Lambda function for C4 diagram generation
"""
import json
import os
import sys

# Add common layer to path
sys.path.insert(0, '/opt/python')

from common.bedrock_client import BedrockClient
from common.validation import validate_input


def build_prompt(context: str) -> str:
    """Build the prompt for Claude to generate C4 diagram."""
    return f"""You are an expert software architect. Based on the following solution context, generate a clear, legible architecture diagram using Mermaid flowchart syntax (NOT C4Context).

Solution Context:
{context}

CRITICAL SYNTAX RULES:
1. Use standard Mermaid flowchart syntax with LEFT-TO-RIGHT (LR) direction
2. Node IDs MUST be simple alphanumeric (no spaces, no special chars): User, S3Bucket, TransferSystem
3. NEVER use reserved words as node IDs: "system", "application", "graph", "class", "end"
4. If you need to use a reserved word, prefix it: node_system, node_application
5. Labels go inside brackets and can have any text: User[👤 User<br/>Uploads files]

CORRECT SYNTAX EXAMPLES:
✓ User[👤 User]
✓ S3Bucket[📦 Amazon S3]
✓ TransferSys[🔷 Transfer System]
✓ SFTPServer[📦 SFTP Server]

TEMPLATE TO FOLLOW:
```
graph LR
    %% Define nodes with clear IDs and styled labels
    UserNode[👤 User<br/>Description]
    MainSystem[🔷 System Name<br/>Description]
    ExternalSvc[📦 External System<br/>Description]
    
    %% Define relationships with clear labels
    UserNode -->|Action description| MainSystem
    MainSystem -->|Action description| ExternalSvc
    
    %% Apply styling
    classDef userStyle fill:#08427B,stroke:#052E56,color:#fff
    classDef systemStyle fill:#1168BD,stroke:#0B4884,color:#fff
    classDef externalStyle fill:#999,stroke:#666,color:#fff
    
    class UserNode userStyle
    class MainSystem systemStyle
    class ExternalSvc externalStyle
```

RULES FOR LEGIBLE DIAGRAMS:
1. ALWAYS use "graph LR" (Left-to-Right) for simple diagrams (≤5 elements)
2. Use "graph TD" (Top-Down) only for complex hierarchies (>5 elements)
3. Keep labels SHORT (max 3-4 words per line)
4. Use <br/> to break long text into multiple lines
5. Add icons: 👤 for users, 🔷 for systems, 📦 for external systems, 💾 for databases
6. Use clear, descriptive relationship labels on arrows
7. Apply consistent styling with classDef

STYLING GUIDE:
- Users/Actors: Dark blue (#08427B)
- Main Systems: Blue (#1168BD)
- External Systems: Gray (#999)
- Databases/Storage: Green (#2E7D32)

Generate a clean, horizontal, legible diagram following these rules. Return ONLY the Mermaid code without markdown code blocks."""


def lambda_handler(event, context):
    """
    Generate C4 diagram from input text
    
    Event body:
    {
        "input_text": "string",
        "diagram_type": "context"
    }
    
    Returns:
    {
        "mermaid_code": "string",
        "validation": {...}
    }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        input_text = body.get('input_text', '')
        
        # Validate input
        validation = validate_input(input_text)
        
        if not validation.is_valid:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'message': 'Validation failed',
                    'errors': validation.errors,
                    'suggestions': validation.suggestions,
                    'questions': validation.questions
                })
            }
        
        # Generate diagram using Bedrock
        bedrock = BedrockClient()
        prompt = build_prompt(input_text)
        
        mermaid_code = bedrock.invoke_claude(prompt, max_tokens=2000)
        
        # Clean up the response - remove markdown code blocks if present
        mermaid_code = mermaid_code.replace("```mermaid\n", "")
        mermaid_code = mermaid_code.replace("```mermaid", "")
        mermaid_code = mermaid_code.replace("```\n", "")
        mermaid_code = mermaid_code.replace("```", "")
        mermaid_code = mermaid_code.strip()
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'mermaid_code': mermaid_code,
                'validation': validation.dict()
            })
        }
        
    except Exception as e:
        print(f"Error generating diagram: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to generate diagram',
                'message': str(e)
            })
        }
