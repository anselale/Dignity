# main.py

from agentforge.utils.DiscordClient import DiscordClient
from agentforge.utils.Logger import Logger  # Import the Logger class
import time
import yaml
from Modules.proccess_slash_command import SlashCommands
from Modules.process_indirect_message import IndirectMessage
from Modules.process_channel_message import ChannelMessage
from Modules.process_direct_message import DirectMessage
from Utilities.Memory import Memory

# Import typing for type annotations
from typing import Optional


class Run:
    def __init__(self):
        """
        Initializes the Run class by setting up the Discord client, loading the persona,
        initializing memory, and setting up message processors.
        """
        # Initialize the Logger
        self.logger: Logger = Logger(name='Run')

        # Declare instance variables with type annotations and default values
        self.client: Optional[DiscordClient] = None
        self.persona: dict = {}
        self.persona_name: str = ''
        self.memory: Optional[Memory] = None
        self.do_command: Optional[SlashCommands] = None
        self.indirect_message: Optional[IndirectMessage] = None
        self.direct_message: Optional[DirectMessage] = None
        self.channel_message: Optional[ChannelMessage] = None

        # Initialize components
        self.initialize_discord_client()
        self.load_persona()
        self.initialize_memory()
        self.initialize_message_processors()
        self.logger.log("Initialization complete.", level='info')

    def initialize_discord_client(self):
        """
        Initializes the Discord client and starts it.
        """
        try:
            self.client = DiscordClient()
            self.client.run()
            self.logger.log("Discord client initialized and running.", level='info')
        except Exception as e:
            self.logger.log(f"Failed to initialize Discord client: {e}", level='error')
            raise

    def load_persona(self):
        """
        Loads the persona configuration from the default YAML file.
        """
        try:
            with open(".agentforge/personas/default.yaml", "r") as file:
                self.persona = yaml.safe_load(file)
                self.persona_name = self.persona.get("Name", "UnknownPersona")
            self.logger.log(f"Persona '{self.persona_name}' loaded successfully.", level='info')
        except FileNotFoundError:
            self.logger.log("Persona YAML file not found.", level='error')
            raise
        except yaml.YAMLError as e:
            self.logger.log(f"Error parsing persona YAML file: {e}", level='error')
            raise
        except Exception as e:
            self.logger.log(f"Unexpected error loading persona: {e}", level='error')
            raise

    def initialize_memory(self):
        """
        Initializes the memory module with the loaded persona.
        """
        try:
            self.memory = Memory(self.persona, self.persona_name)
            self.logger.log("Memory module initialized.", level='info')
        except Exception as e:
            self.logger.log(f"Failed to initialize memory module: {e}", level='error')
            raise

    def initialize_message_processors(self):
        """
        Initializes all the message processing modules.
        """
        try:
            # self.do_command = SlashCommands(self.memory, self.client)
            self.indirect_message = IndirectMessage(self.memory)
            self.direct_message = DirectMessage(self.memory, self.client)
            self.channel_message = ChannelMessage(self.memory, self.client)
            self.logger.log("Message processors initialized.", level='info')
        except Exception as e:
            self.logger.log(f"Failed to initialize message processors: {e}", level='error')
            raise

    def main(self):
        """
        The main loop that continuously processes incoming messages.
        """
        self.logger.log("Starting main loop.", level='info')
        while True:
            try:
                self.process_messages()
            except Exception as e:
                self.logger.log(f"An error occurred during message processing: {e}", level='error')
            finally:
                time.sleep(5)

    def process_messages(self):
        """
        Processes messages from Discord channels.
        """
        try:
            for channel_id, messages in self.client.process_channel_messages():
                for message in messages:
                    self.logger.log(f"Message received in channel {channel_id}: {message}", level='info')
                    self.process_message(message, channel_id)
        except Exception as e:
            self.logger.log(f"Error while processing messages: {e}", level='error')
            raise

    def process_message(self, message, channel_id):
        """
        Determines the type of the message and delegates it to the appropriate handler.
        """
        try:
            function_name = message.get("function_name")
            if function_name:
                # self.handle_slash_command(message, channel_id)
                return  # Early return to avoid unnecessary checks

            if message['channel'].startswith('Direct Message'):
                self.handle_direct_message(message)
                return  # Early return to avoid unnecessary checks

            self.handle_channel_or_indirect_message(message, channel_id)
        except Exception as e:
            self.logger.log(f"Error processing message: {e}", level='error')
            raise

    # def handle_slash_command(self, message, channel_id):
    #     """
    #     Processes slash commands and sends the response as an embedded message.
    #     """
    #     try:
    #         response = self.do_command.parse(message)
    #         self.client.send_embed(
    #             channel_id=channel_id,
    #             title="Command Result",
    #             fields=[("Result", f"{response}")],
    #             color='blue',
    #             image_url=None
    #         )
    #         self.logger.log(f"Slash command '{message.get('function_name')}' processed with response: {response}", level='info')
    #     except Exception as e:
    #         self.logger.log(f"Error handling slash command: {e}", level='error')
    #         raise

    def handle_direct_message(self, message):
        """
        Processes direct messages (DMs) and sends a DM response to the author.
        """
        try:
            response = self.direct_message.process_message(message)
            self.client.send_dm(message['author_id'].id, response)
            self.logger.log(f"Direct message processed for user {message['author_id'].id}.", level='info')
        except Exception as e:
            self.logger.log(f"Error handling direct message: {e}", level='error')
            raise

    def handle_channel_or_indirect_message(self, message, channel_id):
        """
        Determines if the bot is mentioned in the message and handles it accordingly.
        """
        try:
            if self.is_bot_mentioned(message):
                self.handle_channel_message(message, channel_id)
            else:
                self.handle_indirect_message(message)
        except Exception as e:
            self.logger.log(f"Error handling channel or indirect message: {e}", level='error')
            raise

    def handle_channel_message(self, message, channel_id):
        """
        Processes messages where the bot is mentioned directly in a channel.
        """
        try:
            response = self.channel_message.process_message(message)
            self.client.send_message(channel_id, response)
            self.logger.log(f"Channel message processed for channel {channel_id}.", level='info')
        except Exception as e:
            self.logger.log(f"Error handling channel message: {e}", level='error')
            raise

    def handle_indirect_message(self, message):
        """
        Processes messages where the bot is not directly mentioned.
        """
        try:
            self.indirect_message.process_message(message)
            self.logger.log("Indirect message processed: Message was not for the bot.", level='info')
        except Exception as e:
            self.logger.log(f"Error handling indirect message: {e}", level='error')
            raise

    def is_bot_mentioned(self, message):
        """
        Checks if the bot is mentioned in the message.
        """
        return any(mention.name == self.persona_name for mention in message['mentions'])


if __name__ == "__main__":
    try:
        run = Run()
        run.main()
    except Exception as exp:
        # Initialize a basic logger in case Run's logger fails
        fallback_logger = Logger(name='Main')
        fallback_logger.log(f"Fatal error during initialization: {exp}", level='critical')
