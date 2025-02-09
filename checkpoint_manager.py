import os
import json

class CheckpointManager:
    def __init__(self, checkpoint_file):
        self.checkpoint_file = checkpoint_file

    def load(self):
        """Load the checkpoint file and return a set of processed items."""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # data is a dictionary with keys as processed items
                        return set(data.keys())
                    elif isinstance(data, list):
                        # fallback if stored as a list
                        return set(data)
                    else:
                        return set()
            except Exception as e:
                print(f"Error loading checkpoint file {self.checkpoint_file}: {e}")
                return set()
        return set()

    def save(self, processed_set):
        """Save the set of processed items as a dictionary with keys in alphabetical order."""
        data = {item: True for item in processed_set}
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)

    def mark_processed(self, item, processed_set):
        """Add an item to the processed set and save it immediately."""
        processed_set.add(item)
        self.save(processed_set)
