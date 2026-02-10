# 🤖 SC AI Platform Demo

**See how one smart system can power multiple AI applications safely and efficiently**

This interactive demo shows how SC could build a shared AI platform that lets any team add AI features quickly, while keeping everything safe, compliant, and cost-effective.

---

## 📋 What You Need First

- **Python 3.8 or higher** - [Download from python.org](https://python.org) if you don't have it
- **Internet connection** - To download required packages
- **Web browser** - To view the interactive demo

---

## 🚀 Quick Start (3 Simple Steps)

### Step 0: See PII Tokenization Concept (Optional)
```bash
# Quick 30-second demo showing how PII tokenization works
python3 demo_tokenization.py
```
This shows how the platform handles PII with reversible tokens instead of simple masking.

### Step 1: Install Dependencies
```bash
# Open your terminal and navigate to the demo folder
cd /ScalableCapital

# Install required packages
pip3 install -r requirements.txt
```

### Step 2: Launch the Demo
```bash
# Start the interactive demo
python3 -m streamlit run app.py
```

A web browser will automatically open at `http://localhost:8501`

### Step 3: Explore the Platform
Choose a use case, load sample input, and click "Process" to see the AI platform in action!

---

## 🎯 What This Demo Shows

Imagine you could add AI to any business process without hiring developers or worrying about data privacy. That's what this platform does!

**Try 3 real-world examples:**
- **Customer Support Helper** - Automatically sorts customer messages to the right team
- **Document Reader** - Extracts important information from forms and documents
- **HR Assistant** - Answers employee questions about company policies

**The platform automatically handles:**
- 🔒 Protecting sensitive information with **reversible tokenization** (not simple masking)
- 💰 Tracking costs so you know what AI usage costs
- ✅ Making sure AI answers are reliable and accurate
- 📝 Keeping records of everything for compliance

**Key Innovation: Reversible PII Tokenization**
- Unlike simple masking (`email → [REDACTED]`), tokens preserve the ability to use PII
- Backend systems can retrieve original values to send emails, update records, etc.
- UI still shows masked versions for privacy
- Run `python3 demo_tokenization.py` to see this in action!

---

## 🎮 How to Use the Demo

### Basic Usage
1. **Select a use case** from the dropdown menu
2. **Load sample input** or type your own text
3. **Click "Process with AI Platform"**
4. **Explore the tabs** to see how the platform works

**Form Controls:**
- **📝 Load Sample Input** - Loads example text for the selected use case
- **🗑️ Clear Form** - Clears all input and results to start fresh

### Understanding the Results
The demo shows a 4-step pipeline:

**Input Processing Tab:**
- Shows original text and how PII is automatically protected

**Model Selection Tab:**
- Displays which AI model was chosen and processing costs

**Output Tab:**
- Shows the structured AI response with confidence scores
- Indicates if human review is needed

**Audit Log Tab:**
- Complete record of the processing for compliance

### Platform Statistics (Sidebar)
- Total requests processed
- Total and average costs
- Average confidence scores
- Average processing times

---

## 🎨 What You'll Experience

### Support Ticket Classification
**Input:** *"I forgot my password and need help logging in"*

**What happens:**
1. ✅ Checks for private info (none found)
2. 🤖 Chooses GPT-4o-mini model
3. 📝 Gets structured classification
4. 💰 Calculates cost ($0.00001)
5. ✅ Validates response format

**Result:** `{"category": "account_support", "confidence": 0.92}`

### Document Information Extraction
**Input:** Customer onboarding form with personal details

**What happens:**
1. 🔒 Automatically masks emails and account numbers
2. 📋 Extracts key details (name, risk score, etc.)
3. ✅ Ensures output follows required format
4. 📝 Logs everything for compliance

### HR Policy Questions
**Input:** *"What's the maternity leave policy?"*

**What happens:**
1. 🔍 Searches company knowledge base
2. 📖 Provides accurate answer with source citation
3. 📊 Shows confidence level
4. 💰 Tracks usage costs

---

## 💡 Why This Platform Matters

### The Problem: AI Chaos
- ❌ Marketing builds their own chatbot
- ❌ Support builds their own ticket sorter
- ❌ HR builds their own FAQ system
- ❌ Each has different security, costs, and reliability

### The Solution: One Platform for All
- ✅ **Faster development** - Teams configure, don't code
- ✅ **Built-in security** - Automatic PII protection
- ✅ **Cost control** - Shared infrastructure and monitoring
- ✅ **Compliance ready** - Full audit trails
- ✅ **Consistent quality** - Same standards across all AI features

**Impact:** Teams can experiment with AI ideas in hours, not months!

---

## 🔧 Advanced Features

### Using Real AI Models
Want to see it work with actual OpenAI models instead of demo responses?

1. Get a free API key from [OpenAI](https://platform.openai.com)
2. In the demo sidebar, paste your API key
3. The platform will use real GPT-4o-mini and o1-mini models

**Note:** The demo works perfectly without this - we're demonstrating platform architecture, not just AI capabilities.

---

## 🆘 Troubleshooting

### "pip command not found"
```bash
# Try pip3 instead
pip3 install -r requirements.txt
```

### "streamlit command not found"
```bash
# Try running as a Python module
python3 -m streamlit run app.py
```

### "python command not found"
```bash
# Try python3
python3 --version
python3 -m streamlit run app.py
```

### Demo doesn't open in browser
- Look for "Local URL: http://localhost:8501" in terminal
- Open that URL manually in your web browser

### Installation fails
```bash
# Try alternative installation methods
python3 -m pip install -r requirements.txt
# or
pip3 install --user -r requirements.txt
```

### Still having issues?
- Ensure Python 3.8+ is installed
- Check internet connection for package downloads
- Try running in a new terminal window

---

## 📁 Project Structure

```
ScalableCapital/
├── app.py                    # Interactive Streamlit demo
├── gateway.py                # Core AI platform logic with reversible PII tokenization
├── templates.py              # Use case configurations
├── demo_tokenization.py      # Quick demo showing PII tokenization concept
├── test_pipeline.py          # Comprehensive test suite
├── requirements.txt          # Python dependencies
├── DOC/
│   ├── task.md              # Product proposal with PII tokenization concept
│   └── mvp.md               # Technical MVP implementation guide
└── README.md                # This user guide
```

---

## 🎯 The Big Idea

This isn't just a demo - it's a vision for how companies can adopt AI safely at scale. Instead of AI being a "special project," it becomes a normal business capability that any team can use responsibly.

**Built in 2 hours, powers 3 use cases, ready for production!**

---

*Demo created for SC AI Platform Product Manager role - February 2026*