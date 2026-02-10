# 2-Hour MVP Demo - AI Platform POC

## Goal
Prove the platform thesis: **One gateway, multiple use cases, shared guardrails.**

Build a Streamlit demo that shows 3 different AI use cases running through the same platform primitives.

---

## What to Build (120 minutes)

### Core Component: Platform Gateway (30 min)
```python
# gateway.py - ~100 lines
class AIGateway:
    def __init__(self):
        self.pii_vault = {}  # Simple dict for MVP; production uses Redis
    
    def process(self, use_case, input_text, config):
        # 1. PII tokenization (reversible, not one-way masking)
        tokenized_input = self._tokenize_pii(input_text)
        
        # 2. Model routing (based on complexity/cost)
        model = self._route_model(config)
        
        # 3. LLM call with structured output
        response = self._call_llm(model, clean_input, config)
        
        # 4. Schema validation
        validated = self._validate_schema(response, config)
        
        # 5. Audit log
        self._log_audit(use_case, clean_input, validated, cost)
        
        return validated
```

### 3 Use Case Templates (60 min, 20 min each)

**1. Support Ticket Classifier**
- Input: Customer message
- Output: `{category: "billing", confidence: 0.92, reasoning: "..."}`
- Demo: Show same customer question routed to different teams

**2. Document Extractor**
- Input: Mock onboarding form text
- Output: `{name: "...", iban: "[REDACTED]", risk_score: "low"}`
- Demo: Show PII anonymization in action

**3. Internal FAQ Bot**
- Input: Employee question
- Output: `{answer: "...", source: "employee_handbook_p42", confidence: 0.87}`
- Demo: Show confidence-based human fallback

---

## Template Configuration Examples

### Template 1: Support Ticket Classifier
```json
{
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
}
```

### Template 2: Document Extractor
```json
{
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
}
```
**Note:** `fallback_model` uses reasoning (no temperature) - platform strips incompatible params automatically.

### Template 3: Internal FAQ Bot
```json
{
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
  "human_fallback": true
}
```

---

### Streamlit UI (30 min)
- Dropdown to select use case
- Text input
- **Show platform in action:**
  - Original input → PII masked input
  - Model selected (GPT-4o-mini vs GPT-4)
  - Output + confidence score
  - Cost tracker
  - Audit log entry
- **Side panel:** Running totals (requests, avg cost, avg confidence)

---

## Tech Stack (Zero setup complexity)

**Code:**
- Python + Streamlit
- OpenAI Python SDK (use gpt-4o-mini for cost)
- Pydantic (schema validation)
- Re module (PII masking)

**"Database":**
- In-memory list for audit log (demo only)

**Deployment:**
- Run locally: `streamlit run app.py`
- (Optional) Deploy to Streamlit Cloud in 5 min

---

## File Structure

```
/ScalableCapital
├── app.py           # Streamlit UI (80 lines)
├── gateway.py       # Core platform logic (120 lines)
├── templates.py     # 3 use case configs (60 lines)
├── requirements.txt
└── README.md
```

**Total code:** ~260 lines Python

---

## Key Innovation: Reversible PII Tokenization

### The Problem with Simple Masking
Simple PII masking (`email → [REDACTED]`) breaks systems that need to respond to users:
- ❌ Can't send password reset emails (recipient unknown)
- ❌ Can't update user records (original value lost)
- ❌ Can't send notifications (no contact info)

### The Solution: Token-Based Approach
**MVP demonstrates the concept using simple dict storage:**

```python
# 1. Tokenize: Replace PII with reversible tokens
"Contact john@example.com" → "Contact PII_EMAIL_a3f2b1"

# 2. Store mapping (MVP uses dict; production uses Redis)
self.pii_vault["PII_EMAIL_a3f2b1"] = "john@example.com"

# 3. LLM processes tokenized text (compliant)
LLM sees: "Contact PII_EMAIL_a3f2b1"

# 4. Backend retrieves original value when needed
original = self.pii_vault["PII_EMAIL_a3f2b1"]  # "john@example.com"
# Can now actually send emails, update records, etc.

# 5. UI shows masked version for privacy
Display: "Contact j***@example.com"
```

### Production Upgrade Path
- **MVP:** `self.pii_vault = {}` (in-memory dict)
- **Production:** Redis/DynamoDB + AES-256 encryption + 1-hour TTL + access logging

**Demo this:** Run `python3 demo_tokenization.py` to see the flow in action.

---

## Demo Script (What to Show Evaluators)

1. **Support ticket:** Paste "I forgot my password" → Shows routing to "account_support"
2. **Document extraction:** Paste text with email/IBAN → Shows PII redaction + structured output
3. **FAQ:** Ask "What's our parental leave policy?" → Shows answer + source citation
4. **Platform value:**
   - Toggle between use cases = same code path, different config
   - Show audit log = all requests tracked
   - Show cost savings = GPT-4o-mini used 90% of time

**Key insight to communicate:** "This took 2 hours. Each team building this separately = 2 weeks × 10 teams = 20 weeks wasted. Platform thinking."

---

## Build Order (Optimized for 2 hours)

**:00-:30** - Gateway core + PII masking
**:30-:50** - Ticket classifier template
**:50-:70** - Document extractor template  
**:70-:90** - FAQ template
**:90-:120** - Streamlit UI + polish

---

## What NOT to Build

❌ No real API (single-process demo)
❌ No database (in-memory only)
❌ No auth/security
❌ No error handling (happy path only)
❌ No tests
❌ No Terraform
❌ No real Azure deployment

**Why:** Assignment evaluates product thinking, not engineering. This demo proves the concept.

---

## Fallback: If OpenAI API Unavailable

Use mock responses:
```python
def _call_llm(self, model, input, config):
    # Return hardcoded JSON for demo
    return mock_responses[config['template']]
```

Still proves platform architecture works.
