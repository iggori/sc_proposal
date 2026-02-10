import json
import re
import time
from typing import Dict, Any, List
from datetime import datetime
import os

class AIGateway:
    def __init__(self):
        self.audit_log = []
        self.total_cost = 0.0
        self.request_count = 0

    def process(self, use_case: str, input_text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing pipeline"""
        start_time = time.time()

        # 1. PII anonymization
        clean_input = self._anonymize_pii(input_text, config.get('pii_masking', []))

        # 2. Model routing
        model = self._route_model(config)

        # 3. LLM call
        response = self._call_llm(model, clean_input, config)

        # 4. Schema validation
        validated = self._validate_schema(response, config)

        # 5. Calculate cost (mock)
        cost = self._calculate_cost(model, len(clean_input.split()), len(str(validated).split()))

        # 6. Audit log
        self._log_audit(use_case, input_text, clean_input, validated, cost, start_time)

        return {
            'original_input': input_text,
            'cleaned_input': clean_input,
            'model_used': model,
            'output': validated,
            'cost': cost,
            'processing_time': time.time() - start_time
        }

    def _anonymize_pii(self, text: str, pii_types: List[str]) -> str:
        """Basic PII masking with regex"""
        masked_text = text

        if 'email' in pii_types:
            masked_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', masked_text)

        if 'phone' in pii_types:
            masked_text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', masked_text)

        if 'iban' in pii_types:
            # Simple IBAN pattern (DE + 20 digits)
            masked_text = re.sub(r'\b[A-Z]{2}\d{20}\b', '[IBAN_REDACTED]', masked_text)

        return masked_text

    def _route_model(self, config: Dict[str, Any]) -> str:
        """Simple model routing - use fallback if confidence low"""
        base_model = config.get('model', 'gpt-4o-mini')

        # Mock complexity check - if input has many words, use larger model
        # In real implementation, this would analyze input complexity
        complexity_threshold = config.get('complexity_threshold', 100)

        # For demo, randomly choose fallback sometimes
        import random
        if random.random() < 0.3:  # 30% chance
            fallback = config.get('fallback_model')
            if fallback:
                return fallback

        return base_model

    def _call_llm(self, model: str, input_text: str, config: Dict[str, Any]) -> str:
        """Mock LLM call - returns structured JSON based on template type"""
        template = config.get('template')

        # Check for OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)

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

        # Mock responses for demo
        mock_responses = {
            'classification': '''{
                "category": "account_support",
                "confidence": 0.92,
                "reasoning": "User mentions password issues which typically fall under account support"
            }''',
            'extraction': '''{
                "name": "John Smith",
                "email": "[EMAIL_REDACTED]",
                "iban": "[IBAN_REDACTED]",
                "risk_score": "low",
                "nationality": "German"
            }''',
            'qa': '''{
                "answer": "Scalable Capital offers 12 weeks of paid parental leave for primary caregivers and 4 weeks for secondary caregivers, in accordance with German law.",
                "source": "employee_handbook_section_4.2",
                "confidence": 0.87,
                "requires_human_review": false
            }'''
        }

        return mock_responses.get(template, '{"error": "Unknown template"}')

    def _validate_schema(self, response: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Basic JSON validation against schema"""
        try:
            parsed = json.loads(response)
            schema = config.get('output_schema', {})

            # Basic validation - check required fields
            required = schema.get('required', [])
            for field in required:
                if field not in parsed:
                    parsed[field] = f"[MISSING_{field.upper()}]"

            return parsed
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response}

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Mock cost calculation"""
        # Rough estimates per 1K tokens
        costs = {
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'gpt-4o': {'input': 0.0025, 'output': 0.01},
            'o1-mini': {'input': 0.00015, 'output': 0.0006}
        }

        model_costs = costs.get(model, costs['gpt-4o-mini'])
        cost = (input_tokens * model_costs['input'] + output_tokens * model_costs['output']) / 1000
        self.total_cost += cost
        return round(cost, 6)

    def _log_audit(self, use_case: str, original_input: str, clean_input: str,
                   output: Dict[str, Any], cost: float, start_time: float):
        """Log to in-memory audit trail"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'use_case': use_case,
            'original_input_length': len(original_input),
            'cleaned_input_length': len(clean_input),
            'model_used': output.get('model_used', 'unknown'),
            'output_keys': list(output.get('output', {}).keys()) if isinstance(output.get('output'), dict) else [],
            'cost': cost,
            'processing_time': time.time() - start_time,
            'confidence': output.get('output', {}).get('confidence', 0)
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
            'total_cost': round(self.total_cost, 4),
            'avg_cost_per_request': round(self.total_cost / self.request_count, 6) if self.request_count > 0 else 0,
            'avg_confidence': round(avg_confidence, 2),
            'avg_processing_time': round(sum(entry['processing_time'] for entry in self.audit_log) / len(self.audit_log), 2)
        }

    def get_audit_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent audit entries"""
        return self.audit_log[-limit:] if self.audit_log else []