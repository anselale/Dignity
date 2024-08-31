# Modules/process_channel_message.py
from Modules.TrinityLoop import Trinity

class ChannelMessage:

    def __init__(self, memory_instance, discord_client):
        self.memory = memory_instance
        self.discord = discord_client
        self.trinity = Trinity(self.memory, self.discord)
        pass

    def process_message(self, message):
        # await self.discord.set_typing_indicator(message['channel_id'], True)
        self.trinity.do_chat(message)
        # await self.discord.set_typing_indicator(message['channel_id'], False)
        # self.memory.save_channel_simple(message)
        # return f"Responded to {message['message']}"