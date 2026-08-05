#!/usr/bin/env python3
"""
Gemini Go - Core OS Console v3.0 (refactored)
- Improved error handling, logging, typing and HTML sanitization.
- Remove debug residue and reduce risk of showing unsanitized HTML.
"""
import asyncio
import html
import logging
import os
import sys
from datetime import datetime
from typing import Optional

import httpx
import qasync
from google import genai
from google.genai import errors
from googleapiclient.discovery import build
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from supabase import Client, create_client

# ==========================================
# Configuration / Constants
# ==========================================
LOCAL_OLLAMA_URL = os.environ.get("LOCAL_OLLAMA_URL", "http://localhost:11434/api/generate")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GCP_SEARCH_CX = os.environ.get("GCP_SEARCH_CX")
GCP_API_KEY = os.environ.get("GCP_API_KEY")

# Timeouts and retry config
HTTPX_TIMEOUT = 30.0
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 1.0

# Environment check (valid but warn on service role key usage)
ENV_CHECK = bool(SUPABASE_URL and SUPABASE_KEY and GEMINI_API_KEY)
USING_SERVICE_ROLE = bool(os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))

# ==========================================
# Logging
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("gemini_go")

if USING_SERVICE_ROLE:
    logger.warning("SUPABASE_SERVICE_ROLE_KEY detected. Avoid using service role keys in client applications.")

# ==========================================
# Utilities
# ==========================================

def sanitize_for_html(s: str) -> str:
    """Escape text before embedding inside QTextEdit HTML content."""
    return html.escape(s or "")


async def retry_async(func, *args, retries: int = MAX_RETRIES, delay: float = RETRY_DELAY_SECONDS, **kwargs):
    """Simple retry wrapper for async functions."""
    last_exc = None
    for attempt in range(1, retries + 2):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            logger.debug("Attempt %s failed with %s", attempt, e)
            if attempt <= retries:
                await asyncio.sleep(delay)
    raise last_exc


# ==========================================
#  UI / App
# ==========================================
class GeminiGoConsole(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Gemini Go - Core OS Console v3.0")
        self.setMinimumSize(900, 650)

        # Initialize clients only when environment provides keys
        self.supabase: Optional[Client] = None
        self.gemini_client: Optional[genai.Client] = None

        if ENV_CHECK:
            try:
                # Use anon key on clients; service-role keys should be server-side only.
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                logger.info("Cloud clients initialized.")
            except Exception as e:
                logger.exception("Failed to initialize cloud clients: %s", e)
                self.supabase = None
                self.gemini_client = None
        else:
            logger.warning("Missing required environment variables. Some features will be offline.")

        self.init_ui()

    def init_ui(self) -> None:
        """Builds the comprehensive dark-mode developer control panel."""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        self.header_label = QLabel("<b>GEMINI GO // MULTI-MODEL ENGINE MATRIX ACTIVE</b>")
        self.header_label.setStyleSheet("color: #00ffc4; font-size: 13px; letter-spacing: 1px;")
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()

        self.model_selector = QComboBox()
        self.model_selector.addItems(
            [
                "Cloud: gemini-2.5-flash (Speed)",
                "Cloud: gemini-2.5-pro (Deep Code)",
                "Local Motherland: llama3 (Edge)",
            ]
        )
        self.model_selector.setStyleSheet("background-color: #222; color: #00ffc4; border: 1px solid #444; padding: 3px;")
        header_layout.addWidget(self.model_selector)
        layout.addLayout(header_layout)

        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet(
            "background-color: #080808; color: #33ff33; font-family: 'Consolas', monospace; font-size: 13px; border: 1px solid #1a1a1a;"
        )
        self.console_output.setPlaceholderText("Gemini Go Core Framework Loaded. Venom 7.0 Shields Online.")
        layout.addWidget(self.console_output)

        # Input row
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

    def log_to_screen(self, prefix: str, text: str, color_hex: str = "#33ff33") -> None:
        """Append a sanitized HTML-formatted line to the console output."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        safe_prefix = sanitize_for_html(prefix)
        safe_text = sanitize_for_html(text)
        self.console_output.append(f"<span style='color: #555;'>[{timestamp}]</span> <span style='color: {color_hex}; font-weight: bold;'>{safe_prefix}</span> {safe_text}")

    def dispatch_pipeline(self) -> None:
        """Trigger processing of the current command as an asyncio task."""
        raw_text = self.cmd_input.text().strip()
        if not raw_text:
            return
        self.cmd_input.clear()
        # schedule task in event loop handled by qasync
        asyncio.create_task(self.process_command_chain(raw_text))

    # =========================
    # Command routing & handlers
    # =========================
    async def process_command_chain(self, user_input: str) -> None:
        self.run_btn.setEnabled(False)
        self.cmd_input.setEnabled(False)
        selected_engine = self.model_selector.currentText()

        try:
            # Slash-command handling
            if user_input.startswith("/"):
                parts = user_input.split(" ", 1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if command == "/clear":
                    self.console_output.clear()
                elif command == "/history":
                    await self.run_history_fetch()
                elif command == "/search":
                    await self.run_google_search(arg if arg else "Diablo 3")
                elif command == "/activity":
                    await self.run_google_search(f"GCP activity log {arg}")
                else:
                    self.log_to_screen("[Venom Shield]", f"Command '{command}' unregistered.", "#ff3333")
                return

            self.log_to_screen("[User Master Input]", user_input, "#00d2ff")

            # Rebuild context sliding window from Supabase storage
            context = ""
            if self.supabase:
                try:
                    res = self.supabase.table("chat_history").select("user_message, ai_response").order("created_at", desc=True).limit(2).execute()
                    # res.data is expected; guard for unexpected shapes
                    rows = getattr(res, "data", []) or []
                    context = "\n".join([f"User: {r.get('user_message')}\nAI: {r.get('ai_response')}" for r in reversed(rows)])
                except Exception as e:
                    logger.exception("Context sync failed: %s", e)
                    context = f"[Context Sync Lag: {e}]"

            # Route to chosen engine
            if "Local Motherland" in selected_engine:
                await self.execute_local_ollama(user_input, context)
            else:
                model_target = "gemini-2.5-flash" if "flash" in selected_engine else "gemini-2.5-pro"
                await self.execute_cloud_gemini(user_input, context, model_target)

        except Exception as e:
            logger.exception("Global fault intercept: %s", e)
            self.log_to_screen("[Venom Global Fault Intercept]", str(e), "#ff9900")
        finally:
            self.run_btn.setEnabled(True)
            self.cmd_input.setEnabled(True)
            self.cmd_input.setFocus()

    # =========================
    # Execution backends
    # =========================
    async def execute_cloud_gemini(self, user_input: str, context: str, model_name: str) -> None:
        if not self.gemini_client:
            self.log_to_screen("[System]", "Cloud Client offline. Verification credentials missing.", "#ff3333")
            return

        self.log_to_screen(f"[Gemini Cloud Router]", f"Beaming computation request to {model_name}...", "#ffff33")
        full_prompt = f"System: Gemini Go Control Plane Architecture.\nContext Logs:\n{context}\nExecute Order: {user_input}\nOutput:"

        async def _call():
            # blocking call to a sync client - run in executor
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: self.gemini_client.models.generate_content(model=model_name, contents=full_prompt))

        try:
            response = await retry_async(_call)
            # response might be an object with .text, or a dict-like shape - guard both
            ai_text = None
            if hasattr(response, "text"):
                ai_text = getattr(response, "text")
            elif isinstance(response, dict):
                ai_text = response.get("text") or response.get("output") or str(response)
            ai_text = ai_text or "[No text returned by model]"

            # sanitize and display
            self.log_to_screen(f"[{model_name} Response]", ai_text, "#00ff66")

            # Persist to supabase if available; protect against failures
            if self.supabase:
                try:
                    self.supabase.table("chat_history").insert({"user_message": user_input, "ai_response": ai_text}).execute()
                except Exception as e:
                    logger.exception("Failed to insert chat_history: %s", e)
        except errors.APIError as e:
            # Use error.message if available
            msg = getattr(e, "message", str(e))
            logger.warning("Gemini API error: %s", msg)
            self.log_to_screen("[Venom Shield Sandboxed API Error]", msg, "#ff3333")
        except Exception as e:
            logger.exception("Unexpected error calling Gemini: %s", e)
            self.log_to_screen("[Venom Shield Sandboxed API Error]", str(e), "#ff3333")

    async def execute_local_ollama(self, user_input: str, context: str) -> None:
        self.log_to_screen("[Local Edge Router]", "Computing prompt via local port 11434 architecture...", "#ffff33")
        payload = {
            "model": "llama3",
            "prompt": f"System: Local Workspace Context.\nHistory:\n{context}\nInput: {user_input}\nOutput:",
            "stream": False,
        }

        async def _post():
            async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
                return await client.post(LOCAL_OLLAMA_URL, json=payload)

        try:
            response = await retry_async(_post)
            if response.status_code == 200:
                data = response.json()
                # Be defensive with the shape
                ai_text = data.get("response") or data.get("text") or str(data)
                self.log_to_screen("[Local Llama3 Response]", ai_text, "#00ff66")
                if self.supabase:
                    try:
                        self.supabase.table("chat_history").insert({"user_message": user_input, "ai_response": ai_text}).execute()
                    except Exception:
                        logger.exception("Failed to insert local chat_history to supabase")
            else:
                self.log_to_screen("[Local Core Error]", f"HTTP Server Status Code Unacceptable: {response.status_code}", "#ff3333")
        except Exception as e:
            logger.exception("Local model request failed: %s", e)
            self.log_to_screen("[Venom Edge Intercept]", f"Local Core Port Offline. Verify Ollama Status: {str(e)}", "#ff3333")

    # =========================
    # Support features
    # =========================
    async def run_history_fetch(self) -> None:
        if not self.supabase:
            self.log_to_screen("[DB Failure]", "Supabase not configured.", "#ff3333")
            return
        try:
            res = self.supabase.table("chat_history").select("user_message, ai_response").order("created_at", desc=True).limit(3).execute()
            rows = getattr(res, "data", []) or []
            self.console_output.append("\n<span style='color: #b58900;'>--- CLOUD LOG TRANSACTION MATRIX ---</span>")
            for row in reversed(rows):
                self.console_output.append(f"<span style='color: #00d2ff;'>Prompt:</span> {sanitize_for_html(row.get('user_message'))}")
                self.console_output.append(f"<span style='color: #00ff66;'>Response:</span> {sanitize_for_html(row.get('ai_response'))}\n")
        except Exception as e:
            logger.exception("History fetch failed: %s", e)
            self.log_to_screen("[DB Failure]", str(e), "#ff3333")

    async def run_google_search(self, query: str) -> None:
        if not GCP_API_KEY or not GCP_SEARCH_CX:
            self.log_to_screen("[Search Error]", "GCP Search keys not configured.", "#ff3333")
            return
        try:
            loop = asyncio.get_running_loop()
            service = build("customsearch", "v1", developerKey=GCP_API_KEY)
            # run blocking search in executor
            result = await loop.run_in_executor(None, lambda: service.cse().list(q=query, cx=GCP_SEARCH_CX).execute())
            items = result.get("items", []) if isinstance(result, dict) else []
            self.console_output.append(f"\n<span style='color: #cb4b16;'>--- REAL-TIME SEARCH INDEX INDEXES ---</span>")
            for item in items[:2]:
                title = sanitize_for_html(item.get("title", ""))
                link = sanitize_for_html(item.get("link", ""))
                self.console_output.append(f" • <b>{title}</b><br>   <a href='{link}' style='color: #268bd2;'>{link}</a>")
        except Exception as e:
            logger.exception("Search error: %s", e)
            self.log_to_screen("[Search Error]", str(e), "#ff3333")


# ==========================================
# Application entrypoint
# ==========================================

def main() -> None:
    app = QApplication(sys.argv)
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    window = GeminiGoConsole()
    window.show()
    with event_loop:
        event_loop.run_forever()


if __name__ == "__main__":
    main()
