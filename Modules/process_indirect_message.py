# Modules/process_indirect_message.py

class IndirectMessage:

    def __init__(self, memory_instance):
        self.memory = memory_instance
        pass

    def process_message(self, message):
        """
        :param message: -- example object
            {'channel': 'system',
            'channel_id': 1220661170210340894,
            'message': '/bot',
            'author': 'DataBass',
            'author_id':<
                Member id=147043058108596224
                name='dataphreak1001'
                global_name='DataBass'
                bot=False
                nick=None
                guild=<
                    Guild id=147044510768168960
                    name='DataNet'
                    shard_id=0
                    chunked=False
                    member_count=44
                    >
                >,
            'timestamp': '2024-07-28 13:33:48',
            'mentions': []}
        :return:
        """
        try:
            print("Saving...")
            self.memory.save_channel_simple(message)
        except Exception as e:
            print(f"Error saving: {e}")
        return
