# AI Platform MVP Demo

A 2-hour proof-of-concept demonstrating platform thinking for AI infrastructure at Scalable Capital.

## 🎯 What This Proves

**Platform Thesis:** Instead of each team building isolated AI features, provide shared infrastructure that makes AI adoption safe, compliant, and cost-effective at scale.

**Demo Features:**
- ✅ One gateway serving multiple use cases
- ✅ Automatic PII anonymization
- ✅ Model routing (GPT-4o-mini vs GPT-4 vs o1-mini)
- ✅ Schema validation
- ✅ Audit logging with cost tracking
- ✅ Confidence scoring + human fallback logic

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Demo
```bash
streamlit run app.py
```

A browser window will open with the interactive demo.

### 3. Try It Out
1. Select a use case (Support Ticket Classifier, Document Extractor, or FAQ Bot)
2. Click "Load Sample Input" or enter your own text
3. Click "Process with AI Platform"
4. Explore the tabs to see the platform pipeline in action

## 📁 File Structure

```
/ScalableCapital/
├── app.py           # Streamlit UI (main demo interface)
├── gateway.py       # Core platform logic (PII masking, model routing, validation)
├── templates.py     # Use case configurations (JSON schemas, prompts, settings)
├── requirements.txt # Python dependencies
├── mvp.md          # Detailed MVP plan and build instructions
├── task.md         # Main product proposal document
└── task_request.md # Original assignment
```

## 🔧 How It Works

### Platform Pipeline
1. **Input Sanitization** - PII masking (emails, phones, IBANs)
2. **Model Routing** - Choose appropriate model based on complexity/cost
3. **LLM Processing** - Structured generation with prompts and schemas
4. **Output Validation** - JSON schema compliance checking
5. **Audit Logging** - Full traceability for compliance

### Use Cases Demonstrated
- **Support Ticket Classifier** - Routes customer issues to correct teams
- **Document Extractor** - Pulls structured data from onboarding forms
- **Employee FAQ Bot** - Answers HR/policy questions with citations

## 🎮 Demo Scenarios

### Support Ticket Routing
**Input:** "I forgot my password and can't log in"
**Shows:** Classification to "account_support" with confidence scoring

### Document Processing
**Input:** Onboarding form with PII
**Shows:** Automatic redaction + structured extraction

### Knowledge Q&A
**Input:** "What's the parental leave policy?"
**Shows:** Answer with source citation + confidence

## 🔑 Optional: Real OpenAI Integration

To use actual OpenAI models instead of mock responses:

1. Get an OpenAI API key from [platform.openai.com](https://platform.openai.com)
2. In the sidebar, paste your API key
3. The demo will use real GPT-4o-mini/o1-mini models

**Note:** Mock responses work perfectly for the demo - the platform architecture is what matters.

## 📊 Platform Benefits Shown

- **Reusability:** Same code handles 3 different business problems
- **Safety:** PII automatically protected, outputs validated
- **Cost Control:** Model routing + usage tracking
- **Compliance:** Full audit trail for every AI decision
- **Scalability:** Template-based configuration for new use cases

## 🛠️ Technical Details

- **Backend:** Python with modular architecture
- **UI:** Streamlit for rapid prototyping
- **Models:** OpenAI GPT-4o-mini (primary) + o1-mini (reasoning fallback)
- **Validation:** JSON Schema + Pydantic
- **Cost Tracking:** Real-time token usage monitoring

## 🎯 Assignment Context

This MVP demonstrates the core thesis: **AI infrastructure as a product** rather than individual AI features. The platform enables teams to ship AI safely without reinventing guardrails, compliance, or cost controls.

**Time to build:** ~2 hours
**Lines of code:** ~260
**Dependencies:** 3 Python packages

---

*Built for Scalable Capital AI Platform Product Manager assignment - February 2026*