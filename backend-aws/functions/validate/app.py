"""
Lambda function for input validation
"""
import json
import os
import sys

# Add common layer to path
sys.path.insert(0, '/opt/python')

from common.validation import validate_input, ValidationResult


def lambda_handler(event, context):
    """
    Validate input for C4 diagram generation
    
    Event body:
    {
        "input_text": "string"
    }
    
    Returns:
    {
        "is_valid": bool,
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "questions": []
    }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        input_text = body.get('input_text', '')
        
        # Validate
        result = validate_input(input_text)
        
        # Return response
        return {
            'statusCode': 200 if result.is_valid else 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps(result.dict())
        }
        
    except Exception as e:
        print(f"Error in validation: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
