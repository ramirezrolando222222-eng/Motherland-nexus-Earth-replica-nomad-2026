import os
import sys
import asyncio
import httpx
from datetime import datetime, timezone
from google import genai
from google.genai import errors
from supabase import create_client, Client

# =====================================================================
# SYSTEM CORE CONFIGURATION VALIDATION
# =====================================================================
class GeminiCloudOSDaemon:
    """
    Hardened Cloud OS Core Daemon. Handles isolated network request loops,
    asynchronous memory state storage, and dynamic context assembly.
    """
    def __init__(self, fallback_to_local: bool = True):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.local_ollama_url = "http://localhost:11434/api/generate"
        self.fallback_to_local = fallback_to_local

        # Internal Client Interfaces
        self.supabase: Client = None
        self.gemini_client = None
        self.online = False

        self._initialize_system_cores()

    def _initialize_system_cores(self):
        """Validates environment tokens and spins up API connection hooks."""
        if all([self.supabase_url, self.supabase_key, self.gemini_key]):
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                self.gemini_client = genai.Client(api_key=self.gemini_key)
                self.online = True
                print("[SYSTEM INFO] Gemini Cloud OS Daemon cores fully engaged.")
            except Exception as e:
                print(f"[SYSTEM ERROR] Handshake initiation aborted: {str(e)}")
        else:
            print("[SYSTEM WARNING] Missing environment configuration plugs. Operating in isolated local sandbox mode.")

    # =====================================================================
    # MEMORY & CONTEXT SUBSYSTEMS
    # =====================================================================
    async def fetch_session_context(self, history_limit: int = 2) -> str:
        """
        Polls the remote database repository asynchronously using an executor pool 
        to build a contextual sliding window matrix.
        """
        if not self.supabase:
            return "[Context Void: Database Interface Offline]"

        loop = asyncio.get_running_loop()
        try:
            # Offloading blocking Postgrest client requests to thread pool workers
            res = await loop.run_in_executor(
                None,
                lambda: self.supabase.table("chat_history")
                .select("user_message, ai_response")
                .order("created_at", desc=True)
                .limit(history_limit)
                .execute()
            )
            
            if not res.data:
                return "[Context Layer: Empty Registry]"
                
            context_blocks = []
            for record in reversed(res.data):
                context_blocks.append(f"User: {record['user_message']}\nAI: {record['ai_response']}")
            return "\n".join(context_blocks)

        except Exception as e:
            return f"[Context Synchronization Error: {str(e)}]"

    async def commit_to_memory(self, user_prompt: str, system_response: str) -> bool:
        """Archives interaction logs safely to the remote persistent datastore."""
        if not self.supabase:
            return False

        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.supabase.table("chat_history").insert({
                    "user_message": user_prompt,
                    "ai_response": system_response
                }).execute()
            )
            return True
        except Exception as e:
            print(f"[METADATA FAULT] Failed to sync interaction transaction: {str(e)}")
            return False

    # =====================================================================
    # COMPUTE EXECUTION PIPELINES
    # =====================================================================
    async def dispatch_request(self, user_input: str, target_model: str = "gemini-2.5-flash") -> dict:
        """
        Main execution router. Automatically extracts long-term context memory frames,
        routes prompts through thread-isolated workers, and drops back to air-gapped
        local loops if the perimeter gate encounters a network error.
        """
        context_window = await self.fetch_session_context()
        timestamp = datetime.now(timezone.utc).isoformat()

        # Construct safe prompt envelope structure
        system_instructions = (
            "System Control Profile: Hardened Gemini Go Cloud Architecture.\n"
            f"Active Context Boundary:\n{context_window}\n"
            f"Ingress Instruction Channel: {user_input}\n"
            "Execution Output:"
        )

        # Route out to local loop explicitly if cloud is disabled or unconfigured
        if not self.online or "llama" in target_model.lower():
            return await self._execute_local_sandbox(user_input, context_window, timestamp)

        try:
            loop = asyncio.get_running_loop()
            
            # Thread-isolated cloud content synthesis call
            raw_response = await loop.run_in_executor(
                None,
                lambda: self.gemini_client.models.generate_content(
                    model=target_model,
                    contents=system_instructions
                )
            )
            
            generated_text = raw_response.text if raw_response.text else "[Gateway Warning: Empty Content Envelope]"
            
            # Asynchronously fire and forget memory sync call
            asyncio.create_task(self.commit_to_memory(user_input, generated_text))

            return {
                "status": "SUCCESS_CLOUD",
                "model": target_model,
                "timestamp": timestamp,
                "payload": generated_text
            }

        except errors.APIError as api_err:
            print(f"[PERIMETER SHIELD INTERCEPT] Cloud routing failed. HTTP {api_err.code}: {api_err.message}")
            if self.fallback_to_local:
                print("[DAEMON CORE] Initiating emergency local air-gap failover routine...")
                return await self._execute_local_sandbox(user_input, context_window, timestamp)
            raise api_err

    async def _execute_local_sandbox(self, user_input: str, context: str, timestamp: str) -> dict:
        """Executes a thread-safe HTTP routine to a fallback edge container instance."""
        local_payload = {
            "model": "llama3",
            "prompt": f"System Parameter: Local Node Fallback.\nHistory:\n{context}\nInput: {user_input}\nOutput:",
            "stream": False
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(self.local_ollama_url, json=local_payload)
                if res.status_code == 200:
                    output_text = res.json().get("response", "[Local Error: Null Payload]")
                    
                    # Log local workspace actions back to persistence cluster if reachable
                    asyncio.create_task(self.commit_to_memory(user_input, output_text))
                    
                    return {
                        "status": "SUCCESS_LOCAL_EDGE",
                        "model": "llama3-sandbox",
                        "timestamp": timestamp,
                        "payload": output_text
                    }
                return {
                    "status": "CRITICAL_FAULT",
                    "model": "none",
                    "timestamp": timestamp,
                    "payload": f"Local backend server dropped packets. HTTP {res.status_code}"
                }
        except Exception as e:
            return {
                "status": "CRITICAL_FAULT",
                "model": "none",
                "timestamp": timestamp,
                "payload": f"All computing segments unreachable. Loop isolation error: {str(e)}"
            }

# =====================================================================
# INDUSTRIAL TEST RUNTIME ENTRYPOINT
# =====================================================================
if __name__ == "__main__":
    async def main_test_loop():
        # Instantiate engine backend simulator
        daemon = GeminiCloudOSDaemon()
        
        print("\n--- RUNNING DAEMON ROUTING CHANNEL TEST ---")
        response = await daemon.dispatch_request(
            user_input="Write a modular bash script to scan for open terminal instances",
            target_model="gemini-2.5-flash"
        )
        print(f"Execution Status: {response['status']}")
        print(f"Target Compute Unit: {response['model']}")
        print(f"Payload Result:\n{response['payload']}\n")

    # Run the continuous integration test block
    asyncio.run(main_test_loop())
                  # Place this inside your PyQt QMainWindow __init__ constructor block:
self.cloud_os = GeminiCloudOSDaemon()
# Replace your previous code branch router code inside: async def process_command_chain(self, user_input):
if "Local Motherland" in selected_engine:
    engine_tag = "llama3"
else:
    engine_tag = "gemini-2.5-flash" if "flash" in selected_engine else "gemini-2.5-pro"

# Dispatch through your modular daemon engine completely asynchronously
response_package = await self.cloud_os.dispatch_request(user_input, target_model=engine_tag)

# Extract and display the processed system parameters directly to your screen layout
self.log_to_screen(f"[{response_package['model']} Response]", response_package['payload'], "#00ff00")
