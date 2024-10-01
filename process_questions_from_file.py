from Modules.TrinityLoop import Trinity
from Utilities.Memory import Memory
from agentforge.utils.guiutils.discord_client import DiscordClient
import yaml
import time


class Gen_From_File:
    """
    A class to process questions from a file and send them to a Discord channel.

    This class reads questions from a specified file, sends each question to a
    Discord channel, and processes the responses using a Trinity instance.
    """

    def __init__(self, file_path, output_channel_id):
        """
        Initialize the Gen_From_File instance.

        Args:
            file_path (str): The path to the file containing questions.
            output_channel_id (int): The ID of the Discord channel to send messages to.
        """
        self.path = file_path
        self.output_channel_id = output_channel_id
        with open(".agentforge/personas/default.yaml", "r") as file:
            self.persona = yaml.safe_load(file)
            self.persona_name = self.persona.get("Name")
        self.memory = Memory(self.persona, self.persona_name)
        self.discord = DiscordClient()
        self.discord.run()
        time.sleep(30)
        self.trinity = Trinity(self.memory, self.discord)

    def run_file(self):
        """
        Process the file and send each line as a question to the Discord channel.

        This method reads the file, prints each line to the console, sends it to
        the specified Discord channel, and processes the response using Trinity.

        Raises:
            FileNotFoundError: If the specified file is not found.
            IOError: If there's an issue reading the file.
        """
        try:
            with open(self.path, 'r') as file:
                lines = file.readlines()
                print(f'File open:\n{lines}')
            
                for index, line in enumerate(lines, start=1):
                    print(f"{index}. {line.strip()}")
                    response = f'Question: {line}'
                    self.discord.send_message(self.output_channel_id, response)
                    message = {
                        'channel': 'general',
                        'system_message': 'You are a thinking agent responsible for developing a detailed, step-by-step thought process in response to a request, problem, or conversation. Your task is to break down the situation into a structured reasoning process. If feedback is provided, integrate it into your thought process for refinement.',
                        'channel_id': self.output_channel_id,
                        'message': line,
                        'message_id': 1290104562493161527,
                        'author': 'Ansel',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    self.trinity.do_chat(message)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.path}' was not found.")
        except IOError:
            print(f"Error: There was an issue reading the file '{self.path}'.")


# Example usage
if __name__ == "__main__":
    file_path = "text.txt"  # Replace with the actual path to your file
    output_channel_id = 1290496347723661412  # Replace with the desired output channel ID
    print('init gen')
    generator = Gen_From_File(file_path, output_channel_id)
    print('run gen')
    generator.run_file()
    print('gen finished')

