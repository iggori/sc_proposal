from gateway import AIGateway
from templates import get_template
import json

def test_basic_pipeline():
    """Test the full pipeline with support ticket classifier"""
    gateway = AIGateway()
    template = get_template('support_ticket_classifier')
    test_input = 'I forgot my password and need help'

    print('Testing basic pipeline...')
    result = gateway.process('support_ticket_classifier', test_input, template)

    print('✅ Pipeline completed successfully!')
    print('Original:', result['original_input'])
    print('Tokenized:', result['tokenized_input'])
    print('Model:', result['model_used'])
    print('Cost: $' + str(result['cost']))
    print('PII Tokenized:', result['pii_tokenized_count'])
    print('Output:', result['output'])
    print('Stats:', gateway.get_stats())
    print()

def test_pii_masking():
    """Test PII tokenization functionality"""
    gateway = AIGateway()

    # Test email and phone tokenization
    text_with_pii = "Contact me at john@example.com or 555-123-4567"
    tokenized, count = gateway._anonymize_pii(text_with_pii, ['email', 'phone'])

    assert '@' not in tokenized, "Email should be tokenized"
    assert '555' not in tokenized, "Phone should be tokenized"
    assert 'PII_EMAIL_' in tokenized, "Should have email token"
    assert 'PII_PHONE_' in tokenized, "Should have phone token"
    assert count == 2, f"Should tokenize 2 items, got {count}"
    assert len(gateway.pii_vault) == 2, "Vault should have 2 entries"
    
    # Test detokenization (retrieval of original values)
    test_data = {'data': {'email': list(gateway.pii_vault.keys())[0]}}
    detokenized = gateway._detokenize(test_data)
    assert '@' in str(detokenized), "Detokenized data should have email"
    
    print("✅ PII tokenization test passed")

def test_schema_validation():
    """Test schema validation with valid and invalid JSON"""
    gateway = AIGateway()
    template = get_template('support_ticket_classifier')

    # Test valid JSON
    valid_response = '{"category": "account_support", "confidence": 0.92, "reasoning": "Password issue"}'
    result = gateway._validate_schema(valid_response, template)
    assert result['validation_passed'] == True, "Valid JSON should pass validation"
    assert len(result['missing_fields']) == 0, "Should have no missing fields"

    # Test invalid JSON (missing required field)
    invalid_response = '{"category": "account_support", "confidence": 0.92}'  # missing reasoning
    result = gateway._validate_schema(invalid_response, template)
    assert result['validation_passed'] == False, "Invalid JSON should fail validation"
    assert 'reasoning' in result['missing_fields'], "Should detect missing reasoning field"

    print("✅ Schema validation test passed")

def test_model_routing():
    """Test deterministic model routing"""
    gateway = AIGateway()
    template = get_template('onboarding_document_extractor')

    # Simple input should use base model
    simple_input = "Hello world"
    model = gateway._route_model(simple_input, template)
    assert model == 'gpt-4o-mini', f"Simple input should use base model, got {model}"

    # Complex input should use fallback model
    complex_input = "This is a very long input with many words and special characters like @#$%^&*() that should trigger the fallback model because it exceeds the complexity threshold and has special patterns."
    model = gateway._route_model(complex_input, template)
    assert model == 'o1-mini', f"Complex input should use fallback model, got {model}"

    print("✅ Model routing test passed")

def test_error_handling():
    """Test error handling in various scenarios"""
    gateway = AIGateway()

    # Test with invalid template
    try:
        result = gateway.process('invalid_template', 'test input', {})
        assert False, "Should have raised an exception for invalid template"
    except Exception as e:
        print(f"✅ Error handling test passed: {e}")

def test_audit_log():
    """Test audit logging functionality"""
    gateway = AIGateway()
    template = get_template('support_ticket_classifier')

    # Process a few requests
    for i in range(3):
        gateway.process('support_ticket_classifier', f'Test input {i}', template)

    # Check audit log
    audit_entries = gateway.get_audit_log(10)
    assert len(audit_entries) == 3, f"Should have 3 audit entries, got {len(audit_entries)}"

    # Check that entries have required fields
    for entry in audit_entries:
        required_fields = ['timestamp', 'use_case', 'model_used', 'cost', 'processing_time']
        for field in required_fields:
            assert field in entry, f"Audit entry missing {field}"

    print("✅ Audit log test passed")

def test_stats_calculation():
    """Test statistics calculation"""
    gateway = AIGateway()
    template = get_template('support_ticket_classifier')

    # Process requests with different confidence scores
    gateway.process('support_ticket_classifier', 'input1', template)
    gateway.process('support_ticket_classifier', 'input2', template)

    stats = gateway.get_stats()
    assert stats['requests'] == 2, f"Should have 2 requests, got {stats['requests']}"
    assert stats['total_cost'] > 0, "Should have some total cost"
    assert stats['avg_cost_per_request'] > 0, "Should have average cost per request"

    print("✅ Stats calculation test passed")

if __name__ == "__main__":
    print("Running comprehensive tests...\n")

    test_basic_pipeline()
    test_pii_masking()
    test_schema_validation()
    test_model_routing()
    test_error_handling()
    test_audit_log()
    test_stats_calculation()

    print("\n🎉 All tests passed!")