# Modules/challenges.py
import shlex
from typing import List
import requests

class Challenges:

    def __init__(self, memory):
        self.memory = memory
        self.message = None
        self.commands = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]
        self.agents = []

    def parse(self, input, message):
        input_string = input.get('arg')
        self.message = message
        args = shlex.split(input_string)
        if not args:
            return "No command provided. Type 'help' for a list of commands."

        command = args[0].lower()
        if command in self.commands:
            return getattr(self, command)(args[1:])
        else:
            return f"Unknown command: {command}. Type '/bot challenge -?' for a list of commands."

    def level(self, args: List[str] = None):
        user = self.get_or_create_user()
        if args and args[0] == 'list':
            pass
        else:
            level = args[0]
            if user[f'pass-{level}']:
                password = user[f'pass-{level}']
            else:
                password = self.generate_passphrase(3)
                self.memory.save_memory(
                    collection_name='user-table',
                    data=self.message['author_id'].name,
                    ids=user['ids'],
                    metadata={
                        "user_id": self.message['author_id'].id,
                        f"pass-{level}": password,
                    })
            if args[1]:
                message = args[1]
                result = self.run_challenge(level, message, password)
                return result
            else:
                # return doc string
                pass

    def answer(self, args: List[str] = None) -> str:
        pass

    def run_challenge(self, level, message, password):
        agent = self.agents[level]
        agent_vars = {'messages': message, 'password': password}
        result = agent.run(**agent_vars)

        result_message = f"Level{level} Response:\n```{result}```"
        return result_message
        
    @staticmethod
    def get_random_word():
        """Fetch a random English word from the Random Word API."""
        url = "https://random-word-api.herokuapp.com/word?number=1"
        response = requests.get(url)
        if response.status_code == 200:
            word = response.json()[0]
            return word
        else:
            raise Exception("Failed to fetch a random word from the API.")


    def generate_passphrase(self, num_words):
        """Generate a random passphrase with the specified number of words."""
        words = [self.get_random_word() for _ in range(num_words)]
        return ''.join(words)

    def get_or_create_user(self):
        user = self.memory.query_memory(
            collection_name='user-table',
            filter_condition={
                "user_id": self.message['author_id'].id
            }
        )
        if user:
            return user
        else:
            self.memory.save_memory(
                collection_name='user-table',
                data=self.message['author_id'].name,
                metadata={
                    "user_id": self.message['author_id'].id,
                    "exp": 0
                }
            )
