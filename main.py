# main.py

from agentforge.utils.discord.discord_client import DiscordClient
import time
import yaml
from Modules.proccess_slash_command import SlashCommands
from Modules.process_indirect_message import IndirectMessage
from Modules.process_channel_message import ChannelMessage
from Modules.process_direct_message import DirectMessage
from Utilities.Memory import Memory


def process_message(message):
    print(f"Processing message: {message}")
    # Simulate some time-consuming task
    time.sleep(5)
    return f"Processed: -{message}- This process_message function should be replaced."


class Run:

    def __init__(self):
        self.client = DiscordClient()
        self.client.run()
        with open(".agentforge/personas/default.yaml", "r") as file:
            self.persona = yaml.safe_load(file)
            self.persona_name = self.persona.get("Name")
        self.memory = Memory(self.persona, self.persona_name)
        self.do_command = SlashCommands(self.memory, self.client)
        self.indirect_message = IndirectMessage(self.memory)
        self.direct_message = DirectMessage(self.memory, self.client)
        self.channel_message = ChannelMessage(self.memory, self.client)


    def main(self):

        while True:
            try:
                for channel_id, messages in self.client.process_channel_messages():
                    for message in messages:
                        print(f"Message received: {message}")
                        function_name = message.get("function_name")

                        # Check if this is a /bot command
                        if function_name:
                            response = self.do_command.parse(message)
                            # self.client.send_message(channel_id, response)
                            self.client.send_embed(
                                channel_id=channel_id,
                                title="Command Result",
                                fields=[("Result", f"{response}")],
                                color='blue',
                                image_url=None)

                        # Check if the message is a DM
                        elif message['channel'].startswith('Direct Message'):
                            # If it's a DM, use the author's ID to send a DM back
                            response = self.direct_message.process_message(message)
                            self.client.send_dm(message['author_id'].id, response)

                        else:
                            # Check if bot is mentioned in the message
                            mentioned = any(mention.name == self.persona_name for mention in message['mentions'])
                            if mentioned:
                                # If bot is @ mentioned, send the response to the channel
                                # 'Name' in persona must match discord display name.
                                response = self.channel_message.process_message(message)
                                self.client.send_message(channel_id, response)
                            else:
                                self.indirect_message.process_message(message)
                                print('That message was not for me.')
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                time.sleep(5)


if __name__ == "__main__":
    run = Run()
    run.main()
