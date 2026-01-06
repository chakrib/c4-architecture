"""
AWS Bedrock client wrapper for Claude API calls
"""
import boto3
import json
import os
from typing import Dict, Any, List


class BedrockClient:
    """Wrapper for AWS Bedrock Claude API calls"""
    
    def __init__(self, region: str = None):
        self.region = region or os.getenv('BEDROCK_REGION', 'us-east-1')
        self.client = boto3.client('bedrock-runtime', region_name=self.region)
        # Using Claude 3.5 Sonnet for better quality outputs
        self.model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    def invoke_claude(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 1.0,
        system: str = None
    ) -> str:
        """
        Invoke Claude model via Bedrock
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system: System prompt (optional)
        
        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system:
            body["system"] = system
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            print(f"Error invoking Bedrock: {str(e)}")
            raise
    
    def invoke_claude_with_messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 1.0,
        system: str = None
    ) -> str:
        """
        Invoke Claude with full message history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system: System prompt (optional)
        
        Returns:
            Generated text response
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system:
            body["system"] = system
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            print(f"Error invoking Bedrock: {str(e)}")
            raise
