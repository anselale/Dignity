from Modules.TrinityLoop import Trinity
from Utilities.Memory import Memory
from agentforge.utils.guiutils.discord_client import DiscordClient
import yaml
import time


class Gen_From_File:

    def __init__(self, file_path):
        self.path = file_path
        with open(".agentforge/personas/default.yaml", "r") as file:
            self.persona = yaml.safe_load(file)
            self.persona_name = self.persona.get("Name")
        self.memory = Memory(self.persona, self.persona_name)
        self.discord = DiscordClient()
        self.discord.run()
        time.sleep(30)
        self.trinity = Trinity(self.memory, self.discord)

    def run_file(self):
        try:
            with open(self.path, 'r') as file:
                lines = file.readlines()
                print(f'File open:\n{lines}')
            
                for index, line in enumerate(lines, start=1):
                    print(f"{index}. {line.strip()}")
                    response = f'Sending question: {line}'
                    sent_message = self.discord.send_message(self.channel_id_layer_0, response)
                    message = {
                        'channel': 'general',
                        'channel_id': 1287528589251711098,
                        'message': line,
                        'message_id': 1290104562493161527,
                        'author': 'Ansel',
                        'timestamp': '2024-09-30 00:14:56',
                        }
                    self.trinity.do_chat(message)
        
        except FileNotFoundError:
            print(f"Error: The file '{self.path}' was not found.")
        except IOError:
            print(f"Error: There was an issue reading the file '{self.path}'.")


# Example usage
if __name__ == "__main__":
    file_path = "text.txt"  # Replace with the actual path to your file
    print('init gen')
    generator = Gen_From_File(file_path)
    print('run gen')
    generator.run_file()
    print('gen finished')

