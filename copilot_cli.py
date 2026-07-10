#!/usr/bin/env python3
"""
Copilot CLI - Advanced Command Interface
Integrates with free LLM APIs for local and cloud-based AI assistance
Supports: Ollama (local), Groq (free cloud), Hugging Face

Author: Enhanced from Motherland Nexus
License: MIT
"""

import os
import sys
import json
import time
import argparse
from typing import Optional, Dict, Any
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("CopilotCLI")


class APIProvider(Enum):
    """Supported free API providers"""
    OLLAMA = "ollama"
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class OllamaProvider:
    """Local Ollama API provider (completely free, runs locally)"""
    
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
        logger.info(f"Initialized Ollama provider with model: {model}")
    
    def generate(self, prompt: str, stream: bool = False) -> str:
        """Generate response from Ollama"""
        try:
            import requests
        except ImportError:
            logger.error("requests library required. Install with: pip install requests")
            return "Error: requests library not installed"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(self.api_endpoint, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                logger.error(f"API error: {response.status_code}")
                return f"Error: {response.status_code}"
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return f"Error connecting to Ollama. Make sure it's running: ollama serve"
    
    def check_health(self) -> bool:
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


class GroqProvider:
    """Groq API provider (free tier, very fast inference)"""
    
    def __init__(self, model: str = "mixtral-8x7b-32768"):
        self.model = model
        self.api_key = os.environ.get("GROQ_API_KEY")
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set. Get free API key from: https://console.groq.com")
        
        logger.info(f"Initialized Groq provider with model: {model}")
    
    def generate(self, prompt: str) -> str:
        """Generate response from Groq"""
        if not self.api_key:
            return "Error: GROQ_API_KEY not set. Get free key from https://console.groq.com"
        
        try:
            from groq import Groq
        except ImportError:
            logger.error("groq library required. Install with: pip install groq")
            return "Error: groq library not installed"
        
        try:
            client = Groq(api_key=self.api_key)
            message = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
            )
            return message.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return f"Error: {str(e)}"


class HuggingFaceProvider:
    """Hugging Face Inference API provider (free tier available)"""
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        self.model = model
        self.api_key = os.environ.get("HUGGINGFACE_API_KEY")
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        if not self.api_key:
            logger.warning("HUGGINGFACE_API_KEY not set. Get free token from: https://huggingface.co/settings/tokens")
        
        logger.info(f"Initialized HuggingFace provider with model: {model}")
    
    def generate(self, prompt: str) -> str:
        """Generate response from Hugging Face"""
        if not self.api_key:
            return "Error: HUGGINGFACE_API_KEY not set. Get free token from https://huggingface.co/settings/tokens"
        
        try:
            import requests
        except ImportError:
            logger.error("requests library required. Install with: pip install requests")
            return "Error: requests library not installed"
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt}
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "No response generated")
                return str(result)
            else:
                logger.error(f"API error: {response.status_code}")
                return f"Error: {response.status_code}"
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            return f"Error: {str(e)}"


class CopilotCLI:
    """Main Copilot CLI interface"""
    
    def __init__(self, provider: APIProvider = APIProvider.OLLAMA, model: Optional[str] = None):
        self.provider_type = provider
        self.model = model
        self.provider = self._init_provider(provider, model)
        self.history = []
    
    def _init_provider(self, provider: APIProvider, model: Optional[str]) -> Any:
        """Initialize the appropriate API provider"""
        
        if provider == APIProvider.OLLAMA:
            default_model = model or "mistral"
            return OllamaProvider(model=default_model)
        
        elif provider == APIProvider.GROQ:
            default_model = model or "mixtral-8x7b-32768"
            return GroqProvider(model=default_model)
        
        elif provider == APIProvider.HUGGINGFACE:
            default_model = model or "mistralai/Mistral-7B-Instruct-v0.1"
            return HuggingFaceProvider(model=default_model)
        
        else:
            logger.error(f"Unknown provider: {provider}")
            return OllamaProvider()
    
    def ask(self, prompt: str, context: Optional[str] = None) -> str:
        """Ask Copilot a question with optional context"""
        
        if context:
            full_prompt = f"{context}\n\nQuestion: {prompt}"
        else:
            full_prompt = prompt
        
        logger.info(f"Sending prompt to {self.provider_type.value}")
        response = self.provider.generate(full_prompt)
        
        # Store in history
        self.history.append({
            "timestamp": time.time(),
            "prompt": prompt,
            "response": response,
            "provider": self.provider_type.value
        })
        
        return response
    
    def explain_code(self, code: str) -> str:
        """Explain code with context"""
        context = "You are a helpful code assistant. Explain the following code clearly and concisely."
        return self.ask(code, context=context)
    
    def refactor_code(self, code: str) -> str:
        """Suggest refactoring improvements"""
        context = "You are an expert code reviewer. Suggest improvements and refactoring for this code:"
        return self.ask(code, context=context)
    
    def debug_error(self, error: str, code: Optional[str] = None) -> str:
        """Help debug an error"""
        context = "You are an expert debugger. Help me fix this error"
        if code:
            context += f"\n\nCode:\n{code}\n\nError:"
        return self.ask(error, context=context)
    
    def interactive_shell(self):
        """Start interactive CLI session"""
        print("\n" + "="*70)
        print("  🤖 COPILOT CLI - Advanced AI Assistant")
        print(f"  Provider: {self.provider_type.value.upper()}")
        print(f"  Model: {self.model or 'default'}")
        print("="*70)
        print("\nCommands:")
        print("  /help        - Show all commands")
        print("  /explain     - Explain code (paste code, then 'DONE')")
        print("  /refactor    - Suggest refactoring")
        print("  /debug       - Debug an error")
        print("  /history     - Show conversation history")
        print("  /save        - Save conversation")
        print("  /exit        - Exit CLI")
        print("\nOr just type your question and press Enter!\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "/exit":
                    print("\n✨ Goodbye! Your conversation has been saved.")
                    self.save_history()
                    break
                
                elif user_input.lower() == "/help":
                    self._show_help()
                
                elif user_input.lower() == "/history":
                    self._show_history()
                
                elif user_input.lower() == "/save":
                    self.save_history()
                    print("✅ Conversation saved to copilot_history.json")
                
                elif user_input.lower() == "/explain":
                    code = self._get_multiline_input("Paste code (type DONE on new line to finish):\n")
                    if code:
                        response = self.explain_code(code)
                        print(f"\nCopilot: {response}\n")
                
                elif user_input.lower() == "/refactor":
                    code = self._get_multiline_input("Paste code (type DONE on new line to finish):\n")
                    if code:
                        response = self.refactor_code(code)
                        print(f"\nCopilot: {response}\n")
                
                elif user_input.lower() == "/debug":
                    error = input("Paste error message: ").strip()
                    code = input("Paste code (optional, press Enter to skip): ").strip()
                    if error:
                        response = self.debug_error(error, code if code else None)
                        print(f"\nCopilot: {response}\n")
                
                else:
                    # Regular question
                    response = self.ask(user_input)
                    print(f"\nCopilot: {response}\n")
            
            except KeyboardInterrupt:
                print("\n\n✨ Interrupted. Goodbye!")
                self.save_history()
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"❌ Error: {e}\n")
    
    def _get_multiline_input(self, prompt: str) -> str:
        """Get multiline input from user"""
        print(prompt)
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
        return "\n".join(lines)
    
    def _show_help(self):
        """Show help information"""
        print("""
Available Commands:
  /help       - Show this help message
  /explain    - Explain code
  /refactor   - Suggest refactoring
  /debug      - Debug an error
  /history    - Show conversation history
  /save       - Save conversation to file
  /exit       - Exit CLI
  
Just type your question and press Enter for general assistance!
        """)
    
    def _show_history(self):
        """Show conversation history"""
        if not self.history:
            print("No conversation history yet.")
            return
        
        print(f"\n{'='*70}")
        print(f"Conversation History ({len(self.history)} messages)")
        print(f"{'='*70}")
        
        for i, msg in enumerate(self.history, 1):
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['timestamp']))
            print(f"\n[{i}] {timestamp} (via {msg['provider']})")
            print(f"Q: {msg['prompt'][:100]}...")
            print(f"A: {msg['response'][:100]}...")
    
    def save_history(self):
        """Save conversation history to file"""
        if not self.history:
            return
        
        filename = "copilot_history.json"
        with open(filename, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        logger.info(f"History saved to {filename}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🤖 Copilot CLI - Advanced AI Assistant for Developers"
    )
    
    parser.add_argument(
        "--provider",
        choices=["ollama", "groq", "huggingface"],
        default="ollama",
        help="API provider to use (default: ollama)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use (provider-specific)"
    )
    
    parser.add_argument(
        "--ask",
        type=str,
        help="Ask a single question and exit"
    )
    
    parser.add_argument(
        "--explain",
        type=str,
        help="Explain provided code snippet"
    )
    
    parser.add_argument(
        "--refactor",
        type=str,
        help="Suggest refactoring for provided code"
    )
    
    parser.add_argument(
        "--debug",
        type=str,
        help="Debug an error message"
    )
    
    args = parser.parse_args()
    
    # Convert provider string to enum
    provider_map = {
        "ollama": APIProvider.OLLAMA,
        "groq": APIProvider.GROQ,
        "huggingface": APIProvider.HUGGINGFACE,
    }
    
    provider = provider_map.get(args.provider, APIProvider.OLLAMA)
    
    # Initialize CLI
    cli = CopilotCLI(provider=provider, model=args.model)
    
    # Handle single commands
    if args.ask:
        response = cli.ask(args.ask)
        print(response)
    
    elif args.explain:
        response = cli.explain_code(args.explain)
        print(response)
    
    elif args.refactor:
        response = cli.refactor_code(args.refactor)
        print(response)
    
    elif args.debug:
        response = cli.debug_error(args.debug)
        print(response)
    
    else:
        # Start interactive shell
        cli.interactive_shell()


if __name__ == "__main__":
    main()
