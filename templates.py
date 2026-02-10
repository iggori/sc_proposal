import json
from typing import Dict, Any, List

# Template configurations for the AI Platform MVP

TEMPLATES = {
    'support_ticket_classifier': {
        "template": "classification",
        "name": "support_ticket_classifier",
        "model": "gpt-4o-mini",
        "model_params": {
            "temperature": 0.2
        },
        "system_prompt": "You are a support ticket classifier. Categorize the user's issue into one of the predefined categories. Respond ONLY with valid JSON.",
        "categories": ["billing", "account_support", "technical_issue", "product_question"],
        "output_schema": {
            "type": "object",
            "required": ["category", "confidence", "reasoning"],
            "properties": {
                "category": {"type": "string", "enum": ["billing", "account_support", "technical_issue", "product_question"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "reasoning": {"type": "string"}
            }
        },
        "pii_masking": ["email", "phone"],
        "confidence_threshold": 0.85
    },

    'onboarding_document_extractor': {
        "template": "extraction",
        "name": "onboarding_document_extractor",
        "model": "gpt-4o-mini",
        "model_params": {
            "temperature": 0.0
        },
        "system_prompt": "Extract structured information from the onboarding document. Return ONLY valid JSON matching the schema. If a field is not found, use null.",
        "output_schema": {
            "type": "object",
            "required": ["name", "email", "iban", "risk_score"],
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "iban": {"type": "string"},
                "risk_score": {"type": "string", "enum": ["low", "medium", "high"]},
                "nationality": {"type": "string"}
            }
        },
        "pii_masking": ["email", "iban", "phone"],
        "confidence_threshold": 0.90,
        "fallback_model": "o1-mini"
    },

    'employee_faq_bot': {
        "template": "qa",
        "name": "employee_faq_bot",
        "model": "gpt-4o-mini",
        "model_params": {
            "temperature": 0.3,
            "max_tokens": 500
        },
        "system_prompt": "Answer employee questions based on company policies. Always cite the source. If you don't know, say so. Respond with valid JSON.",
        "knowledge_base": "employee_handbook_simplified",
        "output_schema": {
            "type": "object",
            "required": ["answer", "source", "confidence"],
            "properties": {
                "answer": {"type": "string"},
                "source": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "requires_human_review": {"type": "boolean"}
            }
        },
        "pii_masking": ["email", "phone"],
        "confidence_threshold": 0.80,
        "human_fallback": True
    }
}

def get_template(template_name: str) -> Dict[str, Any]:
    """Get template configuration by name"""
    return TEMPLATES.get(template_name)

def get_template_names() -> List[str]:
    """Get list of available template names"""
    return list(TEMPLATES.keys())

def get_template_display_names() -> Dict[str, str]:
    """Get user-friendly display names for templates"""
    return {
        'support_ticket_classifier': 'Support Ticket Classifier',
        'onboarding_document_extractor': 'Document Extractor',
        'employee_faq_bot': 'Employee FAQ Bot'
    }

# Sample input data for demo
SAMPLE_INPUTS = {
    'support_ticket_classifier': "Hi, I forgot my password and can't log into my account. My email is john.doe@example.com and my phone is 555-123-4567. Can you help me reset it?",
    'onboarding_document_extractor': """Onboarding Document
Name: John Smith
Email: john.smith@email.com
Phone: 555-123-4567
IBAN: DE89370400440532013000
Nationality: German
Risk Assessment: Low risk profile""",
    'employee_faq_bot': "What's the parental leave policy at SC?"
}