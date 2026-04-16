import os
import sys
import yaml
import re

# --- DYNAMIC PATH FIX ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)
# ------------------------

from agentforge.agent import Agent
from agentforge.utils.logger import Logger

class ParseFixerAgent(Agent):
    """
    A specialized agent that takes broken YAML strings and the resulting
    error message, and returns sanitized, parseable YAML.
    """
    def __init__(self):
        super().__init__(agent_name="ParseFixerAgent")

class LogParserAgent(Agent):
    """
    AgentForge Agent responsible for converting raw, unstructured log chunks
    into our standardized Dignity YAML format.
    """

    def __init__(self):
        # This will look for .agentforge/agents/LogParserAgent.yaml
        super().__init__(agent_name="LogParserAgent")
        self.logger = Logger(self.__class__.__name__)

    def parse_chunk(self, filename, chunk_data):
        # 1. Prevent empty chunks from crashing the prompt renderer
        if not chunk_data.strip():
            return []

        # Run the LLM
        response = self.run(file_name=filename, log_data=chunk_data)

        if response is None:
            self.logger.log(f"AgentForge returned None for a chunk in {filename}. Skipping.", "error")
            return []

        # 2. If AgentForge successfully auto-parsed it into a list/dict, we're good!
        if isinstance(response, (list, dict)):
            return response

        # 3. If it's a string, it means it needs parsing (or AgentForge failed to parse it internally)
        if isinstance(response, str):
            clean_str = re.sub(r'^```yaml\n|```$', '', response.strip(), flags=re.MULTILINE)

            try:
                # Attempt standard parse
                parsed_data = yaml.safe_load(clean_str)
                return parsed_data if parsed_data else []

            except yaml.YAMLError as initial_error:
                self.logger.log(f"YAML Parse Error detected. Routing to ParseFixerAgent...", "warning")

                # --- THE RECURSIVE SELF-HEALING LOOP (3 STRIKES) ---
                fixer = ParseFixerAgent()
                current_yaml = clean_str
                current_error = str(initial_error)
                max_retries = 3

                for attempt in range(1, max_retries + 1):
                    self.logger.log(f"ParseFixerAgent Attempt {attempt}/{max_retries}...", "info")

                    fixed_raw = fixer.run(raw_yaml=current_yaml, error_msg=current_error)

                    if not fixed_raw:
                        self.logger.log(f"Fixer returned None on attempt {attempt}. Aborting rescue.", "error")
                        break

                    clean_fixed_str = re.sub(r'^```yaml\n|```$', '', fixed_raw.strip(), flags=re.MULTILINE)

                    try:
                        # Try to parse the fixer's new output
                        rescued_data = yaml.safe_load(clean_fixed_str)
                        self.logger.log(f"ParseFixerAgent successfully rescued the data on attempt {attempt}!", "info")
                        return rescued_data if rescued_data else []

                    except yaml.YAMLError as new_error:
                        self.logger.log(f"Fixer attempt {attempt} failed: {new_error}", "warning")
                        # Crucial step: Feed the NEW broken YAML and the NEW error back into the agent for the next loop!
                        current_yaml = clean_fixed_str
                        current_error = str(new_error)

                # If we exhaust all 3 tries without returning:
                self.logger.log(f"ParseFixerAgent exhausted all {max_retries} attempts. Fatal parse failure.", "error")
                return []


class LogOrchestrator:
    """
    Handles file loading, context-window chunking, and merging output.
    """

    def __init__(self, input_dir="raw_logs", output_file="historical_logs.yaml"):
        self.input_dir = input_dir
        self.output_file = output_file
        self.parser_agent = LogParserAgent()
        self.master_log = []
        self.logger = Logger(self.__class__.__name__)

    def chunk_text(self, text, target_lines=75, absolute_max_lines=120):
        """
        Yields chunks of text, splitting safely at logical boundaries
        to avoid severing interactions across two different LLM calls.
        """
        lines = text.split('\n')
        current_chunk = []

        # Heuristic regex to detect the start of a new message turn.
        # Matches formats like "User:", "Dignity:", or "[2023-10-14 12:00] Ansel:"
        speaker_pattern = re.compile(r'^(\[.*?\]\s*)?([a-zA-Z0-9_-]{2,15}:|(user|assistant|human|bot)\s*$)', re.IGNORECASE)

        for i, line in enumerate(lines):
            current_chunk.append(line)

            # Once we hit our target size, start looking for a safe place to cut
            if len(current_chunk) >= target_lines:

                # Check the NEXT line to see if it's a safe boundary
                next_line = lines[i + 1] if i + 1 < len(lines) else ""

                # # Condition 1: The next line is entirely blank (paragraph/interaction break)
                # is_next_blank = (next_line.strip() == '')

                # Condition 2: The next line explicitly starts a new speaker's turn
                is_next_speaker = bool(speaker_pattern.match(next_line))

                # Condition 3: We've gone way over target and are risking the context window
                hit_hard_limit = len(current_chunk) >= absolute_max_lines

                if is_next_speaker or hit_hard_limit or i == len(lines) - 1:
                    yield '\n'.join(current_chunk)
                    current_chunk = []

        # Yield any remaining lines in the final chunk
        if current_chunk:
            yield '\n'.join(current_chunk)

    def process_all_files(self):
        if not os.path.exists(self.input_dir):
            self.logger.log(f"Input directory '{self.input_dir}' not found. Please create it and add logs.", "error")
            return

        try:
            for filename in os.listdir(self.input_dir):
                filepath = os.path.join(self.input_dir, filename)
                if not os.path.isfile(filepath):
                    continue

                print(f"\n" + "=" * 50)
                self.logger.log(f"Reading file: {filename}", "info")
                print("=" * 50)

                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()

                chunks = list(self.chunk_text(file_content, target_lines=75, absolute_max_lines=150))

                for idx, chunk in enumerate(chunks):
                    print(f"\n--- [Chunk {idx + 1}/{len(chunks)} of {filename}] Parsing to LLM ---")

                    parsed_interactions = self.parser_agent.parse_chunk(filename, chunk)

                    if parsed_interactions:
                        for item in parsed_interactions:

                            # Case 1: Stitching severed Bot response
                            if item.get('text') == '[CONTINUED]' and len(self.master_log) > 0:
                                prev_response = self.master_log[-1].get('bot_response') or ''
                                new_response = item.get('bot_response') or ''

                                if prev_response == '[CONTINUED]':
                                    self.master_log[-1]['bot_response'] = new_response
                                else:
                                    self.master_log[-1]['bot_response'] = f"{prev_response}\n\n{new_response}"

                                trunc_stitch = new_response[:40].replace('\n', ' ') + (
                                    '...' if len(new_response) > 40 else '')
                                print(f"  [+] Stitched severed Bot Response -> {trunc_stitch}")

                            # Case 2: Stitching severed User prompt
                            elif item.get('bot_response') == '[CONTINUED]' and len(self.master_log) > 0:
                                prev_text = self.master_log[-1].get('text') or ''
                                new_text = item.get('text') or ''

                                if prev_text == '[CONTINUED]':
                                    self.master_log[-1]['text'] = new_text
                                else:
                                    self.master_log[-1]['text'] = f"{prev_text}\n\n{new_text}"

                                trunc_stitch = new_text[:40].replace('\n', ' ') + ('...' if len(new_text) > 40 else '')
                                print(f"  [+] Stitched severed User Prompt -> {trunc_stitch}")

                            # Case 3: Normal complete interaction pair
                            else:
                                self.master_log.append(item)

                                # Format metrics for the console
                                c_user = item.get('user', 'User')
                                c_date = item.get('date', 'No Date')
                                c_msg = (item.get('text') or '').replace('\n', ' ')
                                c_bot = (item.get('bot_response') or '').replace('\n', ' ')

                                trunc_msg = c_msg[:35] + ('...' if len(c_msg) > 35 else '')
                                trunc_bot = c_bot[:35] + ('...' if len(c_bot) > 35 else '')
                                total_count = len(self.master_log)

                                print(f"  [{total_count:04d}] {c_date} | {c_user}: {trunc_msg} -> Bot: {trunc_bot}")

            # If the loop finishes cleanly, save the master log normally
            self.save_master_log()

        except Exception as e:
            # FATAL CATCH: Dump everything processed up to this millisecond
            self.logger.log(f"CRITICAL ERROR during processing: {e}", "error")
            print(f"\n[!!!] Pipeline crashed. Initiating emergency YAML dump...")

            error_dir = os.path.join(SCRIPT_DIR, "errors")
            os.makedirs(error_dir, exist_ok=True)
            error_file = os.path.join(error_dir, "failed-yaml.yaml")

            with open(error_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.master_log, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            self.logger.log(f"Successfully rescued {len(self.master_log)} interactions to {error_file}", "info")
            print(f"[!!!] Fix the chunk/error and resume processing from the failed file.")

            raise  # Re-raise the error so you can read the actual Python traceback

    def clean_and_merge_log(self):
        """
        Post-processes the master log to heal chunk boundaries and manual splits.
        Strips [CONTINUED] tags and merges orphaned text into the previous block.
        """
        merged_log = []

        for entry in self.master_log:
            user_text = entry.get('text', '')
            bot_text = entry.get('bot_response', '')

            # Detect if this entry is a continuation
            is_cont = '[CONTINUED]' in user_text.upper() or '[CONTINUED]' in bot_text.upper()

            # Clean the tags out (case-insensitive)
            clean_user = re.sub(r'\[(?i)continued\]', '', user_text).strip()
            clean_bot = re.sub(r'\[(?i)continued\]', '', bot_text).strip()

            entry['text'] = clean_user
            entry['bot_response'] = clean_bot

            if is_cont and merged_log:
                # Merge the text into the previous entry
                if clean_user:
                    merged_log[-1]['text'] = f"{merged_log[-1].get('text', '')}\n\n{clean_user}".strip()
                if clean_bot:
                    merged_log[-1]['bot_response'] = f"{merged_log[-1].get('bot_response', '')}\n\n{clean_bot}".strip()

                # Inherit the newer date if available
                if 'date' in entry and entry['date']:
                    merged_log[-1]['date'] = entry['date']
            else:
                # Not a continuation, append as a normal entry
                merged_log.append(entry)

        self.master_log = merged_log

    def save_master_log(self):
        # 1. Clean, strip, and merge the broken chunks BEFORE saving
        self.clean_and_merge_log()

        # 2. Save the perfectly stitched dictionary out to the final YAML file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.master_log, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        self.logger.log(f"Successfully compiled {len(self.master_log)} interactions into {self.output_file}", "info")


if __name__ == "__main__":
    input_directory = os.path.join(SCRIPT_DIR, "raw_logs")
    output_yaml = os.path.join(SCRIPT_DIR, "historical_logs.yaml")

    orchestrator = LogOrchestrator(input_dir=input_directory, output_file=output_yaml)
    orchestrator.process_all_files()