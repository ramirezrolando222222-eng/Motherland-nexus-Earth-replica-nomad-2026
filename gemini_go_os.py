import sys
import os
import asyncio
import qasync
import httpx
from datetime import datetime
from google import genai
from google.genai import errors
from supabase import create_client, Client
from googleapiclient.discovery import build

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, 
                             QVBoxLayout, QWidget, QLineEdit, QLabel, QHBoxLayout, QComboBox)
from PyQt6.QtCore import Qt

# ==========================================
# 1. CORE ENVIRONMENT PLUGS
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GCP_SEARCH_CX = os.environ.get("GCP_SEARCH_CX")
GCP_API_KEY = os.environ.get("GCP_API_KEY")
LOCAL_OLLAMA_URL = "http://localhost:11434/api/generate"

ENV_CHECK = all([SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY])

# ==========================================
# 2. UPGRADED GEMINI GO CONSOLE INTERFACE
# ==========================================
class GeminiGoConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini Go - Core OS Console v3.0")
        self.setMinimumSize(900, 650)
        
        if ENV_CHECK:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            self.supabase, self.gemini_client = None, None

        self.init_ui()

    def init_ui(self):
        """Builds the comprehensive dark-mode developer control panel."""
        layout = QVBoxLayout()

        # System Header Status Bar
        header_layout = QHBoxLayout()
        self.header_label = QLabel("<b>GEMINI GO // MULTI-MODEL ENGINE MATRIX ACTIVE</b>")
        self.header_label.setStyleSheet("color: #00ffc4; font-size: 13px; letter-spacing: 1px;")
        header_layout.addWidget(self.header_label)
        
        header_layout.addStretch()
        
        # Core Model Target Selection Dropdown
        self.model_selector = QComboBox()
        self.model_selector.addItems([
            "Cloud: gemini-2.5-flash (Speed)", 
            "Cloud: gemini-2.5-pro (Deep Code)", 
            "Local Motherland: llama3 (Edge)"
        ])
        self.model_selector.setStyleSheet("background-color: #222; color: #00ffc4; border: 1px solid #444; padding: 3px;")
        header_layout.addWidget(self.model_selector)
        layout.addLayout(header_layout)

        # Main Real-Time Terminal Viewport
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet(
            "background-color: #080808; color: #33ff33; font-family: 'Consolas', monospace; font-size: 13px; border: 1px solid #1a1a1a;"
        )
        self.console_output.setPlaceholderText("Gemini Go Core Framework Loaded. Venom 7.0 Shields Online.")
        layout.addWidget(self.console_output)

        # Execution Command Line Dock
        input_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Type system hook (/search, /activity, /history) or code prompt...")
        self.cmd_input.setStyleSheet("background-color: #121212; color: #fff; padding: 8px; border: 1px solid #333; font-family: monospace;")
        self.cmd_input.returnPressed.connect(self.dispatch_pipeline)
        input_layout.addWidget(self.cmd_input)

        self.run_btn = QPushButton("Execute Task")
        self.run_btn.setStyleSheet("background-color: #007bf5; color: white; font-weight: bold; padding: 8px 18px; border: none;")
        self.run_btn.clicked.connect(self.dispatch_pipeline)
        input_layout.addWidget(self.run_btn)

        layout.addLayout(input_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def log_to_screen(self, prefix: str, text: str, color_hex: str = "#33ff33"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console_output.append(f"<span style='color: #555;'>[{timestamp}]</span> <span style='color: {color_hex}; font-weight: bold;'>{prefix}</span> {text}")

    def dispatch_pipeline(self):
        raw_text = self.cmd_input.text().strip()
        if not raw_text: return
        self.cmd_input.clear()
        asyncio.create_task(self.process_command_chain(raw_text))

    # ==========================================
    # 3. VENOM 7.0 ROUTING MATRIX & SANDBOXING
    # ==========================================
    async def process_command_chain(self, user_input: str):
        self.run_btn.setEnabled(False)
        self.cmd_input.setEnabled(False)
        selected_engine = self.model_selector.currentText()

        try:
            # 1. Intercept Terminal Slash Hooks
            if user_input.startswith('/'):
                parts = user_input.split(' ', 1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if command == '/clear': self.console_output.clear()
                elif command == '/history': await self.run_history_fetch()
                elif command == '/search': await self.run_google_search(arg if arg else "Diablo 3")
                elif command == '/activity': await self.run_google_search(f"GCP activity log {arg}")
                else: self.log_to_screen("[Venom Shield]", f"Command '{command}' unregistered.", "#ff3333")
                return

            # 2. Fall-Through to Selected Model Target
            self.log_to_screen("[User Master Input]", user_input, "#00d2ff")
            
            # Rebuild context sliding window from Supabase storage cords
            context = ""
            if self.supabase:
                try:
                    res = self.supabase.table("chat_history").select("user_message, ai_response").order("created_at", desc=True).limit(2).execute()
                    context = "\n".join([f"User: {r['user_message']}\nAI: {r['ai_response']}" for r in reversed(res.data)])
                except Exception as e:
                    context = f"[Context Sync Lag: {e}]"

            # Execute Model Selection Branching
            if "Local Motherland" in selected_engine:
                await self.execute_local_ollama(user_input, context)
            else:
                model_target = "gemini-2.5-flash" if "flash" in selected_engine else "gemini-2.5-pro"
                await self.execute_cloud_gemini(user_input, context, model_target)

        except Exception as e:
            self.log_to_screen("[Venom Global Fault Intercept]", str(e), "#ff9900")
        finally:
            self.run_btn.setEnabled(True)
            self.cmd_input.setEnabled(True)
            self.cmd_input.setFocus()

    # ==========================================
    # 4. DISTRIBUTED EXECUTION SUBROUTINES
    # ==========================================
    async def execute_cloud_gemini(self, user_input: str, context: str, model_name: str):
        if not self.gemini_client:
            self.log_to_screen("[System]", "Cloud Client offline. Verification credentials missing.", "#ff3333")
            return
        
        self.log_to_screen(f"[Gemini Cloud Router]", f"Beaming computation request to {model_name}...", "#ffff33")
        full_prompt = f"System: Gemini Go Control Plane Architecture.\nContext Logs:\n{context}\nExecute Order: {user_input}\nOutput:"
        
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, lambda: self.gemini_client.models.generate_content(model=model_name, contents=full_prompt)
            )
            ai_text = response.text
            self.log_to_screen(f"[{model_name} Response]", ai_text, "#00ff66")
            
            # Asynchronously archive interaction data straight to your remote database
            if self.supabase:
                self.supabase.table("chat_history").insert({"user_message": user_input, "ai_response": ai_text}).execute()
        except errors.APIError as e:
            self.log_to_screen("[Venom Shield Sandboxed API Error]", e.message, "#ff3333")

    async def execute_local_ollama(self, user_input: str, context: str):
        self.log_to_screen("[Local Edge Router]", "Computing prompt via local port 11434 architecture...", "#ffff33")
        payload = {
            "model": "llama3",
            "prompt": f"System: Local Workspace Context.\nHistory:\n{context}\nInput: {user_input}\nOutput:",
            "stream": False
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(LOCAL_OLLAMA_URL, json=payload, timeout=30.0)
                if response.status_code == 200:
                    ai_text = response.json().get("response", "Error: No text payload extracted.")
                    self.log_to_screen("[Local Llama3 Response]", ai_text, "#00ff66")
                    
                    # Log local sessions to your persistent cloud sync profile as well
                    if self.supabase:
                        self.supabase.table("chat_history").insert({"user_message": user_input, "ai_response": ai_text}).execute()
                else:
                    self.log_to_screen("[Local Core Error]", f"HTTP Server Status Code Unacceptable: {response.status_code}", "#ff3333")
        except Exception as e:
            self.log_to_screen("[Venom Edge Intercept]", f"Local Core Port Offline. Verify Ollama Status: {str(e)}", "#ff3333")

    async def run_history_fetch(self):
        if not self.supabase: return
        try:
            res = self.supabase.table("chat_history").select("user_message, ai_response").order("created_at", desc=True).limit(3).execute()
            self.console_output.append("\n<span style='color: #b58900;'>--- CLOUD LOG TRANSACTION MATRIX ---</span>")
            for row in reversed(res.data):
                self.console_output.append(f"<span style='color: #00d2ff;'>Prompt:</span> {row['user_message']}")
                self.console_output.append(f"<span style='color: #00ff66;'>Response:</span> {row['ai_response']}\n")
        except Exception as e: self.log_to_screen("[DB Failure]", str(e), "#ff3333")

    async def run_google_search(self, query: str):
        if not GCP_API_KEY or not GCP_SEARCH_CX: return
        try:
            loop = asyncio.get_running_loop()
            service = build("customsearch", "v1", developerKey=GCP_API_KEY)
            result = await loop.run_in_executor(None, lambda: service.cse().list(q=query, cx=GCP_SEARCH_CX).execute())
            items = result.get('items', [])
            self.console_output.append(f"\n<span style='color: #cb4b16;'>--- REAL-TIME SEARCH INDEX INDEXES ---</span>")
            for item in items[:2]:
                self.console_output.append(f" • <b>{item['title']}</b><br>   <a href='{item['link']}' style='color: #268bd2;'>{item['link']}</a>")
        except Exception as e: self.log_to_screen("[Search Error]", str(e), "#ff3333")

# ==========================================
# 5. CONSOLE INITIALIZATION RUNTIME
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    window = GeminiGoConsole()
    window.show()
    with event_loop:
        event_loop.run_forever()
      python gemini_go_os.py
