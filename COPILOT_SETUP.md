# Copilot CLI Setup Guide

Complete guide to get your free AI assistant CLI running!

## 🚀 Quick Start (Choose One)

### Option 1: Ollama (Completely Free, Local, No API Key Needed) ⭐ **RECOMMENDED**

**Best for:** Privacy, no costs, offline usage

```bash
# 1. Install Ollama
# macOS/Linux: https://ollama.ai
# Windows: https://ollama.ai/download

# 2. Start Ollama server
ollama serve

# 3. In another terminal, install dependencies
pip install -r requirements.txt

# 4. Run Copilot CLI
python copilot_cli.py --provider ollama

# 5. Try it out
# You: explain this code: def hello(): print("world")
# Copilot: [AI response]
```

**Available Local Models:**
```bash
ollama run mistral          # Fast, 7B parameters
ollama run llama2           # Powerful, 7B/13B/70B options
ollama run neural-chat      # Good for coding
ollama run codellama        # Specialized for code
```

---

### Option 2: Groq API (Free Cloud, Ultra-Fast)

**Best for:** Cloud-based, no local hardware needed, very fast

```bash
# 1. Get free API key
# Go to: https://console.groq.com/keys
# Sign up and copy your API key

# 2. Set environment variable
export GROQ_API_KEY="your-api-key-here"

# 3. Install Groq client
pip install groq

# 4. Run Copilot CLI
python copilot_cli.py --provider groq

# 5. Try it out
```

**Free Groq Models:**
- `mixtral-8x7b-32768` (Very fast, free)
- `llama2-70b-4096` (Powerful)

---

### Option 3: Hugging Face (Free Tier, Many Models)

**Best for:** Access to many models, good for experimentation

```bash
# 1. Get free API token
# Go to: https://huggingface.co/settings/tokens
# Create a new token (read access)

# 2. Set environment variable
export HUGGINGFACE_API_KEY="your-token-here"

# 3. Install requests
pip install requests

# 4. Run Copilot CLI
python copilot_cli.py --provider huggingface

# 5. Try it out
```

---

## 📋 Complete Installation

```bash
# Clone or download your repo
cd Motherland-nexus-Earth-replica-nomad-2026

# Install dependencies
pip install -r requirements.txt

# For Groq support (optional)
pip install groq

# For requests/http support
pip install requests
```

---

## 💻 Usage Examples

### Interactive Mode
```bash
# Default (Ollama)
python copilot_cli.py

# With Groq
python copilot_cli.py --provider groq

# With custom model
python copilot_cli.py --provider ollama --model llama2
```

### Single Question
```bash
python copilot_cli.py --ask "How do I sort a list in Python?"
```

### Explain Code
```bash
python copilot_cli.py --explain "def fibonacci(n): return n if n<=1 else fibonacci(n-1)+fibonacci(n-2)"
```

### Debug Error
```bash
python copilot_cli.py --debug "TypeError: 'NoneType' object is not subscriptable"
```

### Refactor Code
```bash
python copilot_cli.py --refactor "
for i in range(len(list)):
    print(list[i])
"
```

---

## 🎮 Interactive Shell Commands

Once running, use these commands:

```
/help           - Show all commands
/explain        - Explain code (paste code, type DONE)
/refactor       - Suggest improvements
/debug          - Debug an error
/history        - Show conversation history
/save           - Save conversation to JSON
/exit           - Exit CLI
```

**Example Session:**
```
You: /explain
[Paste your code]
DONE
Copilot: [Explanation]

You: Can you optimize that?
Copilot: [Suggestions]

You: /save
✅ Conversation saved to copilot_history.json

You: /exit
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:
```bash
# For Groq
GROQ_API_KEY="your-groq-key"

# For Hugging Face
HUGGINGFACE_API_KEY="your-hf-token"

# For Ollama (optional)
OLLAMA_URL="http://localhost:11434"
```

### Custom Model Configuration

```python
# In your Python code
from copilot_cli import CopilotCLI, APIProvider

# Use Groq with specific model
cli = CopilotCLI(provider=APIProvider.GROQ, model="llama2-70b-4096")

# Use Ollama with custom model
cli = CopilotCLI(provider=APIProvider.OLLAMA, model="codellama")

# Start interactive session
cli.interactive_shell()
```

---

## 🆓 Cost Comparison

| Provider | Cost | Speed | Privacy | Setup |
|----------|------|-------|---------|-------|
| **Ollama** | Free | Medium | 100% Local | Easy |
| **Groq** | Free (with limits) | Very Fast | Cloud | Easy |
| **HuggingFace** | Free (with limits) | Medium | Cloud | Easy |

---

## 🛠️ Troubleshooting

### Ollama not running
```bash
# Make sure Ollama server is active
ollama serve

# In another terminal, verify it's working
curl http://localhost:11434/api/tags
```

### Groq API Error
```bash
# Check if API key is set
echo $GROQ_API_KEY

# Get a new one from https://console.groq.com
```

### HuggingFace Model Too Busy
```bash
# Try a different model or switch to Ollama/Groq
python copilot_cli.py --provider ollama
```

### Memory Issues with Local Models
```bash
# Use smaller model
ollama run mistral     # 7B (faster, less memory)
# Instead of
ollama run llama2:70b  # 70B (slower, more memory)
```

---

## 🚀 Advanced Usage

### Integrate with Your Project

```python
from copilot_cli import CopilotCLI, APIProvider

# In your code
cli = CopilotCLI(provider=APIProvider.GROQ)

# Ask for help
code_explanation = cli.explain_code(your_code)
refactoring_suggestions = cli.refactor_code(your_code)
debug_help = cli.debug_error(error_message, code_context)

# Save conversation
cli.save_history()
```

### Create Aliases

```bash
# Add to your ~/.bashrc or ~/.zshrc
alias copilot="python /path/to/copilot_cli.py"
alias copilot-groq="python /path/to/copilot_cli.py --provider groq"
alias copilot-ollama="python /path/to/copilot_cli.py --provider ollama"

# Then use:
copilot --ask "explain decorators in Python"
```

### Batch Processing

```python
from copilot_cli import CopilotCLI

cli = CopilotCLI()

# Process multiple questions
questions = [
    "What is a closure?",
    "Explain async/await",
    "How does garbage collection work?"
]

for q in questions:
    response = cli.ask(q)
    print(f"Q: {q}")
    print(f"A: {response}\n")

cli.save_history()
```

---

## 📊 Model Recommendations

### For Code Assistance
- **Ollama**: `mistral` or `codellama`
- **Groq**: `mixtral-8x7b-32768`

### For General Questions
- **Ollama**: `llama2`
- **Groq**: `mixtral-8x7b-32768`

### For Speed
- **Groq** (always fastest)

### For Privacy
- **Ollama** (all processing local)

---

## 🎯 Next Steps

1. **Choose a provider** (Ollama recommended for beginners)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Set up your API** (if using Groq/HuggingFace)
4. **Run**: `python copilot_cli.py`
5. **Start asking questions!**

---

## 📝 License

MIT License - See LICENSE file

---

## 💡 Tips

- Save conversations with `/save` for future reference
- Use `/history` to review past interactions
- Try different models to find what works best for you
- Combine with other tools in your development workflow

**Enjoy your free AI assistant! 🚀**
