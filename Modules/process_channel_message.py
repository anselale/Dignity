# Modules/process_channel_message.py
from Modules.TrinityLoop import Trinity

class ChannelMessage:

    def __init__(self, memory_instance, discord_client):
        self.memory = memory_instance
        self.discord = discord_client
        self.trinity = Trinity(self.memory, self.discord)
        pass

    def process_message(self, message):
        self.trinity.do_chat(message)
        # self.memory.save_channel_simple(message)
        return f"Responded to {message['message']}"