from agentforge.utils.chroma_utils import ChromaUtils
from agentforge.utils.functions.Logger import Logger
from Utilities.Parsers import MessageParser

class Memory:

    def __init__(self):
        self.memory = ChromaUtils()
        pass

    def save_channel_simple(self, message):
        channel = message.get('channel')
        message_text = message.get('message')
        author = message.get('author')
        time = message.get('timestamp')
        collection_name = f"a{channel}_chat_history"

        collection_size = self.memory.search_metadata_min_max(collection_name, 'id', 'max')
        if collection_size is None or "target" not in collection_size:
            memory_id = ["1"]
            collection_int = 1
        else:
            memory_id = [str(collection_size["target"] + 1 if collection_size["target"] is not None else 1)]
            collection_int = collection_size["target"] + 1

        metadata = {
            "id": collection_int,
            "User": author,
            "Channel": channel,
            "Timestamp": time
        }

        self.memory.save_memory(collection_name=collection_name,
                                data=message_text,
                                ids=memory_id,
                                metadata=[metadata])
        pass

    def save_dm_simple(self, message):
        channel = message.get('channel')
        message_text = message.get('message')
        author = message.get('author')
        time = message.get('timestamp')
        collection_name = f"dm{author}_chat_history"

        collection_size = self.memory.search_metadata_min_max(collection_name, 'id', 'max')
        if collection_size is None or "target" not in collection_size:
            memory_id = ["1"]
            collection_int = 1
        else:
            memory_id = [str(collection_size["target"] + 1 if collection_size["target"] is not None else 1)]
            collection_int = collection_size["target"] + 1

        metadata = {
            "id": collection_int,
            "User": author,
            "Channel": channel,
            "Timestamp": time
        }

        self.memory.save_memory(collection_name=collection_name,
                                data=message_text,
                                ids=memory_id,
                                metadata=[metadata])
        pass
