import json
import re
import time
import hashlib
from typing import Dict, Any, List, Tuple
from datetime import datetime
import os
from collections import deque

class AIGateway:
    def __init__(self):
        self.audit_log = deque(maxlen=1000)  # Keep last 1000 entries
        self.total_cost = 0.0
        self.request_count = 0
        self.api_key = None  # Store API key securely in instance
        
        # Simple PII vault (demo - production would use Redis/DynamoDB)
        self.pii_vault = {}  # {token: original_value}

        # Pre-compile regex patterns for performance
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),  # US format only for demo
            'iban': re.compile(r'\b[A-Z]{2}\d{20}\b')  # DE format only for demo
        }

        # Model cost constants
        self.MODEL_COSTS = {
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'gpt-4o': {'input': 0.0025, 'output': 0.01},
            'o1-mini': {'input': 0.00015, 'output': 0.0006}
        }

    def set_api_key(self, api_key: str):
        """Securely store API key in instance (not environment)"""
        self.api_key = api_key

    def process(self, use_case: str, input_text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing pipeline with reversible PII handling"""
        start_time = time.time()

        # 1. PII tokenization (reversible)
        tokenized_input, pii_count = self._anonymize_pii(input_text, config.get('pii_masking', []))

        # 2. Model routing
        model = self._route_model(input_text, config)

        # 3. LLM call (with tokenized input)
        response = self._call_llm(model, tokenized_input, config)

        # 4. Schema validation
        validated = self._validate_schema(response, config)

        # 5. Detokenize for backend use (demo concept)
        output_for_backend = self._detokenize(validated)
        output_for_display = self._mask_for_display(validated)

        # 6. Calculate cost (mock)
        cost = self._calculate_cost(model, len(tokenized_input.split()), len(str(validated).split()))

        # 7. Audit log
        self._log_audit(use_case, input_text, tokenized_input, validated, cost, start_time, model, pii_count)

        return {
            'original_input': input_text,
            'tokenized_input': tokenized_input,
            'model_used': model,
            'output': output_for_display,  # For UI (masked)
            'backend_output': output_for_backend,  # For system use (full)
            'cost': cost,
            'processing_time': time.time() - start_time,
            'pii_tokenized_count': pii_count,
            'pii_tokens': list(self.pii_vault.keys())
        }

    def _anonymize_pii(self, text: str, pii_types: List[str]) -> Tuple[str, int]:
        """
        PII tokenization with reversible mapping (MVP demo)
        
        Concept: Replace PII with tokens, store mapping for later retrieval
        Production: Use encrypted Redis/DynamoDB with TTL
        """
        tokenized_text = text
        token_count = 0

        for pii_type in pii_types:
            if pii_type not in self.pii_patterns:
                continue
                
            pattern = self.pii_patterns[pii_type]
            matches = pattern.findall(tokenized_text)
            
            for match in matches:
                # Generate token: PII_EMAIL_abc123
                token = f"PII_{pii_type.upper()}_{hashlib.md5(match.encode()).hexdigest()[:6]}"
                
                # Store mapping (simple dict - production would use secure vault)
                self.pii_vault[token] = match
                
                # Replace in text
                tokenized_text = tokenized_text.replace(match, token, 1)
                token_count += 1

        return tokenized_text, token_count

    def _route_model(self, input_text: str, config: Dict[str, Any]) -> str:
        """Deterministic model routing based on input complexity"""
        base_model = config.get('model', 'gpt-4o-mini')

        # Complexity check based on word count and special characters
        word_count = len(input_text.split())
        complexity_threshold = config.get('complexity_threshold', 100)
        has_complex_patterns = bool(re.search(r'[^\w\s]', input_text))  # Special chars indicate complexity

        # Use fallback model for complex inputs
        if word_count > complexity_threshold or has_complex_patterns:
            fallback = config.get('fallback_model')
            if fallback:
                return fallback

        return base_model

    def _call_llm(self, model: str, input_text: str, config: Dict[str, Any]) -> str:
        """Mock LLM call - returns structured JSON based on template type"""
        template = config.get('template')

        # Check for API key (instance variable, not environment)
        if self.api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)

                # Build messages
                messages = [
                    {"role": "system", "content": config['system_prompt']},
                    {"role": "user", "content": input_text}
                ]

                # Get model params, filter for this model type
                model_params = config.get('model_params', {})
                if model.startswith('o1'):  # Reasoning models don't support temperature
                    model_params = {k: v for k, v in model_params.items() if k not in ['temperature']}

                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **model_params
                )

                return response.choices[0].message.content

            except Exception as e:
                print(f"OpenAI API error: {e}")
                # Fall back to mock

        # Mock responses for demo - preserve tokens from input
        # Extract any PII tokens from input
        tokens_in_input = [token for token in self.pii_vault.keys() if token in input_text]
        email_token = next((t for t in tokens_in_input if 'EMAIL' in t), None)
        phone_token = next((t for t in tokens_in_input if 'PHONE' in t), None)
        iban_token = next((t for t in tokens_in_input if 'IBAN' in t), None)
        
        mock_responses = {
            'classification': '''{
                "category": "account_support",
                "confidence": 0.92,
                "reasoning": "User mentions password issues which typically fall under account support"
            }''',
            'extraction': f'''{{
                "name": "John Smith",
                "email": "{email_token or 'john.smith@email.com'}",
                "iban": "{iban_token or 'DE89370400440532013000'}",
                "risk_score": "low",
                "nationality": "German"
            }}''',
            'qa': '''{
                "answer": "SC offers 12 weeks of paid parental leave for primary caregivers and 4 weeks for secondary caregivers, in accordance with German law.",
                "source": "employee_handbook_section_4.2",
                "confidence": 0.87,
                "requires_human_review": false
            }'''
        }

        return mock_responses.get(template, '{"error": "Unknown template"}')

    def _validate_schema(self, response: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Basic JSON validation against schema - returns validation status"""
        try:
            parsed = json.loads(response)
            schema = config.get('output_schema', {})
            required = schema.get('required', [])

            # Check for missing required fields
            missing_fields = [field for field in required if field not in parsed]

            return {
                'data': parsed,
                'validation_passed': len(missing_fields) == 0,
                'missing_fields': missing_fields
            }
        except json.JSONDecodeError:
            return {
                'data': {"error": "Invalid JSON response", "raw_response": response},
                'validation_passed': False,
                'missing_fields': []
            }

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Mock cost calculation using predefined rates"""
        model_costs = self.MODEL_COSTS.get(model, self.MODEL_COSTS['gpt-4o-mini'])
        cost = (input_tokens * model_costs['input'] + output_tokens * model_costs['output']) / 1000
        self.total_cost += cost
        return round(cost, 6)

    def _log_audit(self, use_case: str, original_input: str, clean_input: str,
                   output: Dict[str, Any], cost: float, start_time: float, model_used: str, pii_masked_count: int):
        """Log to in-memory audit trail"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'use_case': use_case,
            'original_input_length': len(original_input),
            'cleaned_input_length': len(clean_input),
            'pii_masked_count': pii_masked_count,
            'model_used': model_used,
            'output_keys': list(output.get('data', {}).keys()) if isinstance(output, dict) and 'data' in output else [],
            'cost': cost,
            'processing_time': time.time() - start_time,
            'confidence': output.get('data', {}).get('confidence', 0) if isinstance(output, dict) and 'data' in output else 0,
            'validation_passed': output.get('validation_passed', False) if isinstance(output, dict) else False
        }

        self.audit_log.append(entry)
        self.request_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get platform statistics"""
        if not self.audit_log:
            return {'requests': 0, 'total_cost': 0, 'avg_confidence': 0}

        avg_confidence = sum(entry.get('confidence', 0) for entry in self.audit_log) / len(self.audit_log)

        return {
            'requests': self.request_count,
            'total_cost': round(self.total_cost, 6),  # Show microcents
            'avg_cost_per_request': round(self.total_cost / self.request_count, 6) if self.request_count > 0 else 0,
            'avg_confidence': round(avg_confidence, 2),
            'avg_processing_time': round(sum(entry['processing_time'] for entry in self.audit_log) / len(self.audit_log), 2)
        }

    def get_audit_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent audit entries"""
        if not self.audit_log:
            return []
        # Convert deque to list and get last 'limit' items
        return list(self.audit_log)[-limit:]
    
    def _detokenize(self, data: Any) -> Any:
        """
        Replace PII tokens with original values for backend processing
        
        Example: {"email": "PII_EMAIL_abc123"} -> {"email": "john@example.com"}
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == 'data' and isinstance(value, dict):
                    result[key] = self._detokenize(value)
                elif isinstance(value, str) and value.startswith('PII_'):
                    result[key] = self.pii_vault.get(value, value)
                else:
                    result[key] = value
            return result
        return data
    
    def _mask_for_display(self, data: Any) -> Any:
        """
        Replace PII tokens with masked values for UI display
        
        Example: {"email": "PII_EMAIL_abc123"} -> {"email": "j***@example.com"}
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == 'data' and isinstance(value, dict):
                    result[key] = self._mask_for_display(value)
                elif isinstance(value, str) and value.startswith('PII_'):
                    original = self.pii_vault.get(value, value)
                    if '@' in original:
                        # Email: john@example.com -> j***@example.com
                        parts = original.split('@')
                        result[key] = f"{parts[0][0]}***@{parts[1]}"
                    elif original.replace('-', '').replace('.', '').isdigit():
                        # Phone: 555-123-4567 -> ***-***-4567
                        result[key] = '***-***-' + original[-4:]
                    else:
                        result[key] = original[:2] + '***'
                else:
                    result[key] = value
            return result
        return data