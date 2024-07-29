# Modules/process_channel_message.py

class ChannelMessage:

    def __init__(self, memory_instance):
        self.memory = memory_instance
        pass

    def process_message(self, message):
        self.memory.save_channel_simple(message)
        return f"Responding to {message['message']}"