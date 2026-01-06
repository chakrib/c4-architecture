"""
AI service for interacting with Anthropic Claude API.
"""
import anthropic
import json
from django.conf import settings
from .schemas import SuggestionOption, ValidationResult


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


def generate_diagram(input_text: str) -> str:
    """Generate Mermaid diagram code using Claude."""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        raise Exception("Anthropic API key not configured")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = build_prompt(input_text)
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        mermaid_code = message.content[0].text.strip()
        
        # Clean up the response - remove markdown code blocks if present
        mermaid_code = mermaid_code.replace("```mermaid\n", "")
        mermaid_code = mermaid_code.replace("```mermaid", "")
        mermaid_code = mermaid_code.replace("```\n", "")
        mermaid_code = mermaid_code.replace("```", "")
        mermaid_code = mermaid_code.strip()
        
        return mermaid_code
        
    except Exception as e:
        raise Exception(f"Failed to generate diagram: {str(e)}")


def generate_improvement_suggestions(original_text: str, validation_result: ValidationResult) -> list[SuggestionOption]:
    """Use Claude to generate improved versions of the input text."""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        return []
    
    prompt = f"""You are an expert at translating business/technical descriptions into C4 Context diagram requirements.

A user provided this description:
"{original_text}"

This description has validation issues:
{', '.join(validation_result.errors + validation_result.questions)}

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

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        response_data = json.loads(response_text)
        
        suggestions = []
        for item in response_data.get("suggestions", []):
            suggestions.append(SuggestionOption(
                title=item["title"],
                description=item["description"],
                improved_text=item["improved_text"]
            ))
        
        return suggestions
        
    except Exception as e:
        print(f"Error generating suggestions: {str(e)}")
        return []


def refine_diagram(current_mermaid: str, original_context: str, refinement_instruction: str) -> dict:
    """Use Claude to refine an existing Mermaid diagram."""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        raise Exception("Anthropic API key not configured")
    
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

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        response_data = json.loads(response_text)
        
        return response_data
        
    except Exception as e:
        raise Exception(f"Failed to refine diagram: {str(e)}")
