# Modules/process_channel_message.py
from Modules.DignityFlow import Dignity


class ChannelMessage:

    def __init__(self, memory_instance, discord_client):
        self.memory = memory_instance
        self.discord = discord_client
        self.dignity = Dignity(self.memory, self.discord)
        pass

    def process_message(self, message):
        self.dignity.do_chat(message)


# from Modules.TrinityLoop import Trinity
#
#
# class ChannelMessage:
#
#     def __init__(self, memory_instance, discord_client):
#         self.memory = memory_instance
#         self.discord = discord_client
#         self.trinity = Trinity(self.memory, self.discord)
#         pass
#
#     def process_message(self, message):
#         self.trinity.do_chat(message)
