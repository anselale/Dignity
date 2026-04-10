import os
import sys
import yaml
import datetime

# --- DYNAMIC PATH FIX ---
# Define where this script lives, and where the Dignity root is
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# Add root to sys.path so Python can find 'Modules' and 'Utilities'
sys.path.insert(0, PROJECT_ROOT)

# Change working directory to root so AgentForge can find '.agentforge'
os.chdir(PROJECT_ROOT)
# ------------------------

from Modules.TrinityLoop import Trinity
from Utilities.Memory import Memory


def ingest_yaml_with_cognition(trinity_instance, yaml_file_path, target_user="User", target_user_id="000000"):
    """
    Feeds raw logs through Trinity's Thought and Theory agents to generate
    rich experiential data before saving to memory.
    """

    # 1. Silence the UI so it doesn't attempt to send Discord messages during processing
    trinity_instance.ui.send_message = lambda *args, **kwargs: None

    if not os.path.exists(yaml_file_path):
        print(f"[!] Error: Could not find {yaml_file_path}")
        return

    # 2. Load the YAML data
    with open(yaml_file_path, 'r', encoding='utf-8') as file:
        chat_logs = yaml.safe_load(file)

    total_logs = len(chat_logs)
    print(f"\n" + "=" * 60)
    print(f"Starting cognitive ingestion of {total_logs} interactions for {target_user}...")
    print("=" * 60 + "\n")

    try:
        for i, entry in enumerate(chat_logs):
            trinity_instance.reset_cognition()

            # --- NEW: Extract and set the historical date ---
            # Fallback to today's date if the YAML is missing it, just to prevent crashes
            historical_date = entry.get('date', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Pass the date to our overridden memory class!
            trinity_instance.memory.set_historical_date(historical_date)
            # ------------------------------------------------

            # --- CONSOLE METRICS ---
            c_msg = (entry.get('text') or '').replace('\n', ' ')
            c_bot = (entry.get('bot_response') or '').replace('\n', ' ')

            trunc_msg = c_msg[:35] + ('...' if len(c_msg) > 35 else '')
            trunc_bot = c_bot[:35] + ('...' if len(c_bot) > 35 else '')

            print(
                f"  [{i + 1:04d}/{total_logs:04d}] {historical_date} | {target_user}: {trunc_msg} -> Bot: {trunc_bot}")
            # -----------------------

            # 3. Construct the Message Dictionary
            # Now it forces the target_user and target_user_id you pass in, overriding any fillers
            mock_message = {
                'channel': 'Historical_Import',
                'channel_id': 'import_01',
                'author': target_user,
                'author_id': target_user_id,
                'message': entry.get('text') or '',
                'message_id': str(i),
                'attachments': []
            }

            trinity_instance.message = mock_message

            print(f"[{i + 1}/{len(chat_logs)}] Generating cognition for message from {mock_message['author']}...")

            # 4. Fetch Histories
            trinity_instance.cognition['scratchpad'] = trinity_instance.memory.get_scratchpad(mock_message['author'])

            self_scratchpad = trinity_instance.memory.get_self_scratchpad()
            trinity_instance.cognition['self_scratchpad'] = self_scratchpad
            trinity_instance.chat_history, trinity_instance.unformatted_history = trinity_instance.memory.fetch_history(
                collection_name=mock_message['channel'])
            trinity_instance.user_history, trinity_instance.unformatted_user_history = trinity_instance.memory.fetch_history(
                collection_name=mock_message['author'], query=mock_message['message'], is_user_specific=True, query_size=3)
            trinity_instance.dm_history, trinity_instance.unformatted_dm_history = trinity_instance.memory.fetch_history(
                collection_name=mock_message['author'], query=mock_message['message'], is_user_specific=True, query_size=3,
                prefix='dm')

            # 5. Run the Thought Agent
            trinity_instance.run_agent('thought')

            # 6. Execute Journal and Category memory operations
            if 'thought' in trinity_instance.cognition and 'Categories' in trinity_instance.cognition['thought']:
                categories = trinity_instance.cognition['thought']["Categories"]
                trinity_instance.cognition['thought']["Categories"] = trinity_instance.memory.category_replace(categories)
                trinity_instance.memory.recall_journal_entry(trinity_instance.message['message'],
                                                             trinity_instance.cognition['thought']["Categories"], 3)
                trinity_instance.category_memory = trinity_instance.memory.recall_categories(
                    trinity_instance.message['message'], trinity_instance.cognition['thought']["Categories"], 3)

            trinity_instance.cognition['scratchpad'] = trinity_instance.memory.get_scratchpad(
                trinity_instance.message['author'])

            # 7. Run the Theory Agent
            # trinity_instance.run_agent('theory')

            # 8. Inject the historical response (Bypass Generate & Reflect)
            historical_response = entry.get('bot_response', '')
            trinity_instance.response = historical_response

            # Populate the generate dictionary just in case your memory pipeline expects it
            trinity_instance.cognition['generate'] = {'result': historical_response}

            # 9. Save all memories
            trinity_instance.save_memories()
            # 1. Save the interaction to the scratchpad logs so the counter goes up
            trinity_instance.memory.save_scratchpad_log(mock_message['author'], mock_message['message'],
                                                        historical_response)
            trinity_instance.memory.save_self_scratchpad_log()

            # 2. Save the interaction to the journal log
            # (Note: save_channel_memory usually does this, so we must add it manually here)
            trinity_instance.memory.save_to_collection('journal_log_table', mock_message, historical_response, {})

            # 3. Check and trigger the Agents if thresholds (10 or 100) are met
            trinity_instance.memory.check_scratchpad(mock_message['author'])
            trinity_instance.memory.check_self_scratchpad()
            trinity_instance.memory.check_journal()

        print("Cognitive historical ingestion complete. All logs are now rich memories.")

    except Exception as e:
        # FATAL CATCH: Dump the REMAINING logs so the user can resume
        print(f"\n[!!!] CRITICAL ERROR during ingestion: {e}")
        print(f"[!!!] Pipeline crashed at entry {i + 1}. Initiating emergency YAML dump...")

        error_dir = os.path.join(SCRIPT_DIR, "errors")
        os.makedirs(error_dir, exist_ok=True)
        error_file = os.path.join(error_dir, "unprocessed-import.yaml")

        # Slice the list from the current failed index to the end
        remaining_logs = chat_logs[i:]

        with open(error_file, 'w', encoding='utf-8') as f:
            yaml.dump(remaining_logs, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"[+] Successfully rescued {len(remaining_logs)} unprocessed interactions to {error_file}")
        print(f"[+] To resume, fix the issue, point the script to '{error_file}', and run again.")
        raise


class DummyClient:
    def __init__(self):
        self.user = self.DummyUser()

    class DummyUser:
        def __init__(self):
            self.id = "999999999"
            self.name = "Dignity_Offline"

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class HistoricalMemory(Memory):
    def __init__(self, persona, persona_name):
        super().__init__(persona, persona_name)
        self.current_historical_date = None
        self.last_seen_date = None
        self.time_offset_seconds = 0

        # 1. Locate the AgentForge Chroma Storage instance
        self.storage = self.memory

        # 2. TURN OFF AGENTFORGE AUTO-TIMESTAMPS DYNAMICALLY
        if hasattr(self.storage, 'config'):
            self.storage.config.settings.storage['options']['iso_timestamp'] = False
            self.storage.config.settings.storage['options']['unix_timestamp'] = False
            print("[+] Successfully disabled AgentForge's auto-timestamping for historical import.")

        self._override_chroma_storage()

    def set_historical_date(self, date_string):
        if date_string != self.last_seen_date:
            self.last_seen_date = date_string
            self.time_offset_seconds = 0
        self.current_historical_date = date_string

    def _override_chroma_storage(self):
        self.original_save_method = self.storage.save_to_storage

        def historical_save_wrapper(*args, **kwargs):
            import uuid
            import datetime

            # 1. Extract arguments safely regardless of how Memory.py passes them
            collection_name = kwargs.pop('collection_name', args[0] if len(args) > 0 else None)
            data = kwargs.pop('data', args[1] if len(args) > 1 else None)
            ids = kwargs.pop('ids', args[2] if len(args) > 2 else None)
            metadata = kwargs.pop('metadata', args[3] if len(args) > 3 else None)

            # 2. FORCE DATA TO BE A LIST (Fixes the length mismatch bug)
            if data is None:
                data = []
            elif not isinstance(data, list):
                data = [data]

            data_len = len(data)

            # 3. FORCE IDS TO BE A LIST OF THE EXACT SAME LENGTH
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(data_len)]
            elif not isinstance(ids, list):
                ids = [ids]

            # Pad ids if too short, trim if too long
            if len(ids) < data_len:
                ids.extend([str(uuid.uuid4()) for _ in range(data_len - len(ids))])
            elif len(ids) > data_len:
                ids = ids[:data_len]

            # 4. FORCE METADATA TO BE A LIST OF DICTS OF THE EXACT SAME LENGTH
            if metadata is None:
                metadata = [{} for _ in range(data_len)]
            elif not isinstance(metadata, list):
                metadata = [metadata]

            # Pad metadata if too short, trim if too long
            if len(metadata) < data_len:
                metadata.extend([{} for _ in range(data_len - len(metadata))])
            elif len(metadata) > data_len:
                metadata = metadata[:data_len]

            # 5. INJECT OUR HISTORICAL TIMESTAMPS
            for i in range(data_len):
                if not isinstance(metadata[i], dict):
                    metadata[i] = {}

                if self.current_historical_date:
                    try:
                        date_str = str(self.current_historical_date)
                        if len(date_str) <= 10:
                            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        else:
                            dt = datetime.datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        dt = datetime.datetime.now()
                else:
                    dt = datetime.datetime.now()

                dt = dt + datetime.timedelta(seconds=self.time_offset_seconds)

                # Inject into the dictionary so it's never empty
                metadata[i]['iso_timestamp'] = dt.strftime("%Y-%m-%d %H:%M:%S")
                metadata[i]['unix_timestamp'] = dt.timestamp()

            # Tick the clock forward so the next entry is 1 second later
            self.time_offset_seconds += 1

            # 6. PASS THE NORMALIZED LISTS TO CHROMADB
            return self.original_save_method(
                collection_name=collection_name,
                data=data,
                ids=ids,
                metadata=metadata,
                **kwargs  # Pass any remaining safe kwargs
            )

        self.storage.save_to_storage = historical_save_wrapper


# --- Execution ---
if __name__ == "__main__":
    dummy_client = DummyClient()

    with open(".agentforge/personas/default.yaml", "r") as file:
        persona = yaml.safe_load(file)
        persona_name = persona.get("Name")

    memory = HistoricalMemory(persona, persona_name)

    trinity = Trinity(memory, dummy_client)

    target_yaml = os.path.join(SCRIPT_DIR, "historical_logs.yaml")

    ingest_yaml_with_cognition(
        trinity_instance=trinity,
        yaml_file_path=target_yaml,
        target_user="DataBass",
        target_user_id="147043058108596224"
    )