# Modules/challenges.py

import shlex
from typing import List
import requests
import os
import importlib


def create_function_list(folder_path):
    agent_object = {}

    # Iterate over the files in the specified folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".py"):
            # Remove the ".py" extension to get the module name
            module_name = file_name[:-3]

            # Import the module dynamically
            module = importlib.import_module(f"{folder_path.replace('/', '.')}.{module_name}")

            # Iterate over the classes defined in the module
            for class_name, class_obj in module.__dict__.items():
                if isinstance(class_obj, type) and class_name != 'Agent':
                    # Create an instance of the class
                    agent_instance = class_obj()

                    # Add the instance to the agent_object dictionary
                    agent_object[class_name] = agent_instance

    return agent_object


class Challenges:

    def __init__(self, memory):
        self.memory = memory.memory
        self.message = None
        self.commands = ['level', 'answer', 'reset']
        agents_path = "CustomAgents/Levels"
        self.agents = create_function_list(agents_path)
        print(f"Agent Object: {self.agents}")

    def parse(self, user_input, message):
        # remove this
        print(f"User Input: {user_input}\nString Test: {user_input[1:]}")

        input_string = user_input[0]
        self.message = message
        args = user_input[1:]
        if not args:
            return "No command provided. Type 'help' for a list of commands."

        command = input_string
        if command in self.commands:
            result = getattr(self, command)(args)
            print(f"result in challenges: {result}")
            return result
        else:
            return f"Unknown command: {command}. Type '/bot challenge -?' for a list of commands."

    def level(self, args: List[str] = None):
        print(f"Test args: {args}")
        user = self.get_or_create_user()
        print(f"get user success: {user}")

        if args and args[0] == 'list':
            # Get a list of the keys in the agent_object dictionary
            agent_keys = list(self.agents.keys())

            # Create a string with each key on a separate line
            agent_keys_string = "\n".join(agent_keys)

            # We can add a description later
            return agent_keys_string
        elif args and args[0] == '-?':
            level_help_string = """
            Syntax:
            /bot challenge level <LevelName> list - List all available levels
            /bot challenge level <LevelName> - Get a hint about a specific level
            /bot challenge level <LevelName> "text" - Sends attack text as a prompt to the LLM prompt for that level.
                (Quotes required)
            /bot challenge level <LevelName> reset - Resets the level, it's password, and any EXP you have gained
                from that specific level.
            """
            return level_help_string
        else:
            # get level requested
            print(f"level else: {args[0]}")
            level = args[0]

            # Does user have a generated password for this level?
            try:
                pass_level = user['metadatas'][0].get(f'pass-{level}', False)
            except:
                print("No pass for this level")
                pass_level = None
            if pass_level:
                print("trying to assign password")
                password = user['metadatas'][0][f'pass-{level}']

            # If not, generate password and store it in the database.
            else:
                print("create password")
                password = self.generate_passphrase(3)
                print(f"Password: {password}\nUserId: {user['ids']}")
                self.memory.save_memory(
                    collection_name='user-table',
                    data=[self.message['author_id'].name],
                    ids=[str(self.message['author_id'].id)],
                    metadata=[{
                        "user_id": self.message['author_id'].id,
                        f"pass-{level}": password
                    }])

            # If answer is provided, run challenge prompt
            print("testing hint")
            try:
                args1 = args[1]
            except:
                args1 = None
            if args1:
                message = args[1]
                print(f"Run challenge: {message}")
                result = self.run_challenge(level, message, password)
                return result

            # Otherwise, return challenge hint.
            else:
                # return doc string from agent containing hint
                print("retrieving hint")
                hint = self.hint(level)
                print(f"hint retirieved: {hint}")
                return hint

    def answer(self, args: List[str] = None):
        print(f"Starting answer. Args: {args}")
        # Check provided password against stored password.
        user = self.get_or_create_user()
        level = args[0]
        try:
            complete = user['metadatas'][0][f'{level}-complete']
        except:
            complete = False
        try:
            args1 = args[1]
        except:
            args1 = None
        if args[0] == "-?":
            answer_help_text = """
            Send an answer attempt for the specified level.
            All answers will be 3 random words, all lowercase no space.
            Syntax:
                /bot challenge answer <LevelName> <answer>
            Note: Attempts to brute force will be considered spam.
            """
            return answer_help_text
        elif args1 == user['metadatas'][0][f'pass-{level}'] and complete is not True:
            # Update EXP, return correct
            try:
                exp = user['metadatas'][0]['exp']
            except:
                exp = 0
            self.memory.save_memory(
                collection_name='user-table',
                data=self.message['author_id'].name,
                ids=[str(self.message['author_id'].id)],
                metadata=[{
                    "user_id": self.message['author_id'].id,
                    "exp": exp+50,
                    f"{level}-complete": True
                }]
            )

            # Placeholder. Actual experience should be based on challenge difficulty.
            correct_string = f"Success! You have {exp+50} experience! You are level {int((exp+50)//100)}."
            return correct_string
        elif complete is True:
            completed_string = f"""
            You have already completed this challenge. 
            To reset, type: /bot challenge reset {level}
            This will remove the exp you gained from completeting this challenge.
            """
            return completed_string

        else:
            similarity = self.calculate_similarity(args[1], user['metadatas'][0][f'pass-{level}'])
            fail_string = f"Incorrect. Please try again.\nSimilarity: {int(similarity)}%"
            return fail_string

    def run_challenge(self, level, message, password):
        print(f"Agents: {self.agents}")
        agent = self.agents[level]
        agent_vars = {'user_message': message, 'password': password}
        print(f"running agent: {agent_vars}\nRunning Level: {level}")
        result = agent.run(**agent_vars)

        result_message = f"Level {level} Response:\n{result}"
        print(f"Result message from agent: {result_message}")
        # try:
        #     split = shlex.split(result_message)
        #     print(f"Split: {split}")
        # except:
        #     split = None
        # if password in split:
        #     print(f"Saving result")
        #     self.memory.save_memory(
        #         collection_name='solution-table',
        #         data=message,
        #         metadata=[{
        #             "user_id": self.message['author_id'].id,
        #             "user_name": self.message['author_id'].name,
        #         }])
        #     print("Result saved")
        print("Returning result message")
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
        user = self.memory.load_collection(
            collection_name='user-table',
            where={
                "user_id": self.message['author_id'].id
            }
        )
        if user:
            return user
        else:
            self.memory.save_memory(
                collection_name='user-table',
                data=[self.message['author_id'].name],
                ids=[str(self.message['author_id'].id)],
                metadata=[{
                    "user_id": self.message['author_id'].id,
                    "exp": 0
                }]
            )
            user = self.memory.load_collection(
                collection_name='user-table',
                filter_condition={
                    "user_id": self.message['author_id'].id
                }
            )
            return user

    def hint(self, level) -> str:
        print(f"starting level hint: {level}")
        hint_text = f"Level {level} Hint:\n"
        print(hint_text)
        level_string = str(level)
        if level_string in self.agents:
            agent = self.agents[level_string]
            doc = agent.__doc__
        else:
            doc = 'Agent not found.'
        # doc = getattr(self, self.agents[level_string]).__doc__
        print(f"Doc: {doc}")
        hint_text += f"  {level}: {doc.strip() if doc else 'No description available.'}\n"
        print(f"Returning hint_text: {hint_text}")
        return hint_text

    @staticmethod
    def calculate_similarity(str1, str2):
        # Initialize variables
        len1 = len(str1)
        len2 = len(str2)
        max_len = max(len1, len2)
        min_len = min(len1, len2)
        match_count = 0

        # Iterate over the characters of the shorter string
        for i in range(min_len):
            if str1[i] == str2[i]:
                match_count += 1

        # Calculate the similarity percentage
        similarity_percentage = (match_count / max_len) * 100

        return similarity_percentage

    def reset(self,args: List[str] = None):
        new_pass = self.generate_passphrase(3)
        level = args[0]
        user = self.get_or_create_user()
        pass_level = user['metadatas'][0].get(f'{level}-complete')
        current_exp = user['metadatas'][0].get('exp')
        if pass_level and pass_level is True:
            self.memory.save_memory(
                collection_name='user-table',
                data=self.message['author_id'].name,
                ids=[str(self.message['author_id'].id)],
                metadata=[{
                    "user_id": self.message['author_id'].id,
                    "exp": current_exp - 50,
                    f"{level}-complete": False,
                    f"pass-{level}": new_pass
                }]
            )
            reset_text = f"""
                Level {level} reset. Your exp was {current_exp}.
                It is now {current_exp - 50}. A new pass phrase has been generated for this level.
                """
        elif args[0] == "-?":
            reset_help_text = """
            Resets a specified level. EXP gained from that level will be lost.
            Resetting a level that has not been complete will only reset the answer and not deduct EXP.
            Syntax:
                /bot challenge reset <LevelName>
            """
            return reset_help_text
        else:
            reset_text = "This level is not complete. We have reset the password, but there was no deduction to EXP."
            self.memory.save_memory(
                collection_name='user-table',
                data=self.message['author_id'].name,
                ids=[str(self.message['author_id'].id)],
                metadata=[{
                    "user_id": self.message['author_id'].id,
                    f"{level}-complete": False,
                    f"pass-{level}": new_pass
                }]
            )
        return reset_text
