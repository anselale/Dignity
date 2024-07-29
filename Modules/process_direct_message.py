# Modules/process_direct_message.py

class DirectMessage:

    def __init__(self, memory_instance):
        self.memory = memory_instance
        pass

    def process_message(self, message):
        self.memory.save_dm_simple(message)
        return f"Responding to {message['message']}"