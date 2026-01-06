"""
Input validation logic for C4 diagram generation
"""
from typing import List, Dict
from pydantic import BaseModel


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []
    questions: List[str] = []


def validate_input(text: str) -> ValidationResult:
    """
    Validate input for C4 diagram generation.
    Focus on identifying minimum requirements for C4 Level 1.
    
    C4 Level 1 (Context Diagram) requires:
    1. The System being built (mandatory)
    2. Users/Actors who interact with it (mandatory)
    3. External systems it integrates with (optional but helpful)
    """
    errors = []
    warnings = []
    suggestions = []
    questions = []
    
    # Check for empty input
    if not text or not text.strip():
        errors.append("Empty input provided")
        suggestions.append("Please describe the system you want to build")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    # Check minimum word count (15 words)
    words = text.split()
    word_count = len(words)
    
    if word_count < 15:
        errors.append(f"Input too short ({word_count} words). Need at least 15 words for meaningful C4 diagram.")
        suggestions.append("Please provide more details about:")
        suggestions.append("  • What system/application are you building?")
        suggestions.append("  • Who will use it?")
        suggestions.append("  • What does it do?")
        suggestions.append("  • What external systems does it connect to?")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    text_lower = text.lower()
    
    # Check for gibberish - look for meaningful words
    meaningful_words = [
        # Actions
        'build', 'create', 'develop', 'make', 'design', 'implement', 'deploy',
        # Systems
        'system', 'application', 'app', 'service', 'platform', 'tool', 'software',
        'web', 'mobile', 'api', 'backend', 'frontend', 'dashboard', 'website', 'portal', 'interface',
        # Users
        'user', 'users', 'customer', 'customers', 'admin', 'administrator', 'client', 'clients',
        'people', 'person', 'employee', 'staff', 'developer', 'manager', 'operator', 'visitor', 'member',
        # Common tech terms
        'data', 'database', 'server', 'cloud', 'storage', 'file', 'files', 'upload', 'download',
        'authentication', 'authorization', 'payment', 'order', 'process', 'manage', 'track',
        'send', 'receive', 'store', 'retrieve', 'display', 'show', 'view', 'edit', 'delete',
        # Business terms
        'business', 'company', 'organization', 'team', 'department', 'workflow', 'process',
        'report', 'analytics', 'dashboard', 'notification', 'alert', 'message', 'email',
        # Integration terms
        'integrate', 'connect', 'sync', 'transfer', 'import', 'export', 'api', 'webhook'
    ]
    
    meaningful_count = sum(1 for word in meaningful_words if word in text_lower)
    
    # If less than 3 meaningful words in 15+ words, likely gibberish
    if meaningful_count < 3:
        errors.append("Input appears to be gibberish or lacks technical/business context")
        suggestions.append("Please describe a real system or application using clear language")
        suggestions.append("Example: 'Build a web application where users can upload documents, store them in cloud storage, and share them with team members'")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    # C4 Level 1 Requirements Check
    
    # 1. Check for THE SYSTEM (what are we building?)
    system_indicators = [
        'build', 'create', 'develop', 'make', 'design', 'implement',
        'system', 'application', 'app', 'service', 'platform', 'tool', 'software',
        'web', 'mobile', 'api', 'backend', 'frontend', 'dashboard',
        'website', 'portal', 'interface'
    ]
    
    has_system = any(indicator in text_lower for indicator in system_indicators)
    
    if not has_system:
        errors.append("Cannot identify what system/application you want to build")
        questions.append("What type of system are you building? (e.g., web app, mobile app, API service, platform)")
        suggestions.append("Please specify the system you want to create")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    # 2. Check for USERS/ACTORS (who uses it?)
    user_indicators = [
        'user', 'users', 'customer', 'customers', 'admin', 'administrator',
        'client', 'clients', 'people', 'person', 'employee', 'staff',
        'developer', 'manager', 'operator', 'visitor', 'member', 'team'
    ]
    
    has_users = any(indicator in text_lower for indicator in user_indicators)
    
    if not has_users:
        # This is critical for C4 Level 1 - ask a question
        questions.append("Who will use this system? (e.g., customers, employees, administrators)")
        warnings.append("C4 Context diagrams require identifying the users/actors")
        suggestions.append("Add information about who will interact with the system")
    
    # 3. Check for FUNCTIONALITY (what does it do?)
    functionality_indicators = [
        'upload', 'download', 'store', 'retrieve', 'process', 'manage', 'track',
        'send', 'receive', 'display', 'show', 'view', 'edit', 'delete', 'create',
        'update', 'search', 'filter', 'sort', 'analyze', 'report', 'notify',
        'authenticate', 'authorize', 'pay', 'order', 'book', 'schedule', 'share',
        # Dashboard and analytics verbs
        'determine', 'identify', 'monitor', 'visualize', 'review', 'assess', 'evaluate',
        'compare', 'measure', 'calculate', 'aggregate', 'summarize', 'forecast',
        'predict', 'detect', 'discover', 'explore', 'inspect', 'examine',
        # Data interaction verbs
        'generate', 'produce', 'compile', 'collect', 'gather', 'extract', 'transform',
        'load', 'import', 'export', 'sync', 'integrate', 'consolidate',
        # User actions
        'access', 'browse', 'navigate', 'select', 'choose', 'configure', 'customize',
        'submit', 'approve', 'reject', 'request', 'respond', 'comment', 'collaborate'
    ]
    
    has_functionality = any(indicator in text_lower for indicator in functionality_indicators)
    
    if not has_functionality:
        questions.append("What will users do with this system? What are the main features?")
        warnings.append("No clear functionality described")
        suggestions.append("Describe what users can do with the system")
    
    # 4. Check for EXTERNAL SYSTEMS (optional but helpful)
    external_indicators = [
        'integrate', 'connect', 'sync', 'api', 'database', 'storage', 's3', 'aws',
        'google', 'microsoft', 'salesforce', 'stripe', 'paypal', 'twilio',
        'slack', 'email', 'sms', 'webhook', 'third-party', 'external',
        # Specific services
        'whatsapp', 'gmail', 'docs', 'sheets', 'drive', 'dropbox', 'box',
        'azure', 'gcp', 'firebase', 'supabase', 'mongodb', 'postgresql', 'mysql',
        'redis', 'elasticsearch', 'kafka', 'rabbitmq', 'sendgrid', 'mailchimp',
        'zendesk', 'jira', 'confluence', 'github', 'gitlab', 'bitbucket',
        'shopify', 'woocommerce', 'magento', 'wordpress', 'hubspot'
    ]
    
    has_external = any(indicator in text_lower for indicator in external_indicators)
    
    if not has_external:
        warnings.append("No external systems or integrations mentioned")
        suggestions.append("Consider mentioning: databases, cloud storage, third-party APIs, or external services")
    
    # If we have critical questions, mark as invalid and ask for clarification
    if questions:
        errors.append("Insufficient information for C4 Context diagram")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    # If we only have warnings but no questions, it's valid but could be better
    return ValidationResult(is_valid=True, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
