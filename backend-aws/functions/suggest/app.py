"""
Lambda function for generating improvement suggestions
"""
import json
import os
import sys

# Add common layer to path
sys.path.insert(0, '/opt/python')

from common.bedrock_client import BedrockClient
from common.validation import validate_input


def lambda_handler(event, context):
    """
    Generate improvement suggestions for incomplete input
    
    Event body:
    {
        "input_text": "string"
    }
    
    Returns:
    {
        "original_text": "string",
        "validation_issues": [],
        "suggestions": [
            {
                "title": "string",
                "description": "string",
                "improved_text": "string"
            }
        ]
    }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        input_text = body.get('input_text', '')
        
        # Validate input
        validation = validate_input(input_text)
        
        # If already valid, no need for suggestions
        if validation.is_valid:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Input is already valid. Use /api/diagrams/generate instead.'
                })
            }
        
        # If gibberish or too short, don't generate suggestions
        if any("gibberish" in error.lower() or "too short" in error.lower() for error in validation.errors):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Cannot generate suggestions for this input',
                    'errors': validation.errors,
                    'suggestions': validation.suggestions
                })
            }
        
        # Generate suggestions using Bedrock
        bedrock = BedrockClient()
        
        prompt = f"""You are an expert at translating business/technical descriptions into C4 Context diagram requirements.

A user provided this description:
"{input_text}"

This description has validation issues:
{', '.join(validation.errors + validation.questions)}

For C4 Level 1 (Context) diagrams, we need:
1. THE SYSTEM being built (what software/service)
2. USERS/ACTORS (who uses it)
3. FUNCTIONALITY (what does it do)
4. EXTERNAL SYSTEMS (what does it integrate with)

Based on the user's description, generate 3 different interpretations that would be suitable for C4 diagrams. Each should be a complete, clear description (50-100 words) that includes all 4 required elements.

Format your response as JSON:
{{
  "suggestions": [
    {{
      "title": "Brief title (5-7 words)",
      "description": "One sentence explaining this interpretation",
      "improved_text": "Complete description with system, users, functionality, and external systems"
    }},
    ... (2 more suggestions)
  ]
}}

Make the suggestions diverse - consider different angles like:
- Enforcement/prevention system
- Monitoring/auditing tool
- Automation/provisioning service
- Governance/compliance platform

Return ONLY the JSON, no other text."""
        
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
            'body': json.dumps({
                'original_text': input_text,
                'validation_issues': validation.errors + validation.questions,
                'suggestions': response_data.get('suggestions', [])
            })
        }
        
    except Exception as e:
        print(f"Error generating suggestions: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to generate suggestions',
                'message': str(e)
            })
        }
