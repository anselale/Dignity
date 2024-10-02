# Modules/process_slash_modules.py

import shlex
from typing import List
from Modules.challenges import Challenges


class SlashCommands:
    def __init__(self, memory_instance, discord_client):
        self.memory = memory_instance
        self.discord = discord_client
        self.message = None
        self.challenges = Challenges(self.memory)
        self.commands = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__") and func != "parse"]

    def parse(self, message):
        input_string = message.get('arg')
        self.message = message
        args = shlex.split(input_string)
        if not args:
            return "No command provided. Type 'help' for a list of commands."

        command = args[0].lower()
        if command == '-?':
            return self.help([""])
        if command in self.commands:
            return getattr(self, command)(args[1:])
        else:
            return f"Unknown command: {command}. Type 'help' for a list of commands."

    def help(self, args: List[str] = None) -> str:
        """
        This command.
        """
        if args and args[0] == '-?':
            return "help: Lists all available commands or get help for a specific command."

        help_text = "Available commands:\n"
        for cmd in self.commands:
            doc = getattr(self, cmd).__doc__
            help_text += f"  {cmd}: {doc.strip() if doc else 'No description available.'}\n"
            help_text += f"\nType /bot command -? for instructions for specific commands"
        return help_text

    def echo(self, args: List[str]) -> str:
        """Repeat the given text."""
        if args and args[0] == '-?':
            return "echo: Repeat the given text.\nUsage: echo [text]"
        return " ".join(args)

    def add(self, args: List[str]) -> str:
        """Add two numbers."""
        if args and args[0] == '-?':
            return "add: Add two numbers.\nUsage: add [number1] [number2]"
        if len(args) != 2:
            return "Error: Add requires exactly two arguments."
        try:
            return str(float(args[0]) + float(args[1]))
        except ValueError:
            return "Error: Both arguments must be numbers."

    def challenge(self, args: List[str]) -> str:
        """
        A collection of capture the flag challenges. The bot has a secret
        password hidden in their system prompt. Your job is to get them to
        reveal the secret password, which you can turn in for points.
        """
        if args and args[0] == '-?':
            return """
            challenge: Prompt attack capture the flag
            Usage:
                /bot challenge level list - List of challenges and descriptions
                /bot challenge level <LevelName> - Get the challenge hint text
                /bot challenge level <LevelName> "text" - Send the text to the challenge as part of the prompt attack.
                /bot challenge answer <LevelName> - Attempt to answer the specified level..
                /bot challenge reset <LevelName> - Resets the specified level.
            """
        else:
            result = self.challenges.parse(args, self.message)
            print(f"Result in process command: {result}")
            return result

    @staticmethod
    def about():
        """
        About the bot.
        """
        return """
            This project was built using AgentForge, an open-source AI-driven task automation 
            system created by John Smith and Ansel Anselmi. AgentForge is available at 
            https://github.com/DataBassGit/AgentForge under the GNU General Public License v3.0.
            """

    # def test_roles(self, args: List[str]) -> str:
    #     """
    #     Test role management functions.
    #     Usage: test_roles <guild_id> <user_id> [role_name]
    #     """
    #     if args and args[0] == '-?':
    #         return ("test_roles: Test role management functions.\n"
    #                 "Usage: test_roles <guild_id> <user_id> [role_name]")
    #
    #     guild_id = self.message['author_id'].guild.id
    #     print(f'Guild ID: {guild_id}')
    #     user_id = self.message['author_id'].id
    #     print(f'User ID: {user_id}')
    #     role_name = "TestRole"
    #
    #     results = []
    #
    #     # List all roles in the guild and for the user
    #     print(f'Testing List Roles')
    #     roles_info = self.discord.list_roles(guild_id, user_id)
    #     print(f'List Roles finished')
    #     results.append(f"Roles information:\n{roles_info}")
    #
    #     # Add a role to the user
    #     print(f'Testing Add Role')
    #     add_result = self.discord.add_role(guild_id, user_id, role_name)
    #     print(f'Add Role finished')
    #     results.append(f"Add role result: {add_result}")
    #
    #     # Check if the user has the role
    #     print('Testing Has Role')
    #     has_role = self.discord.has_role(guild_id, user_id, role_name)
    #     print('Has Role Finished')
    #     results.append(f"User has role '{role_name}': {has_role}")
    #
    #     # Remove the role from the user
    #     print('Testing Remove Role')
    #     remove_result = self.discord.remove_role(guild_id, user_id, role_name)
    #     print('Remove role finished')
    #     results.append(f"Remove role result: {remove_result}")
    #
    #     # Check again if the user has the role
    #     print('Testing Has Role after removal')
    #     has_role = self.discord.has_role(guild_id, user_id, role_name)
    #     print('Has Role Finished')
    #     results.append(f"User has role '{role_name}' after removal: {has_role}")
    #
    #     return "\n\n".join(results)

    # def test_kb(self, args):
    #     results = self.memory.query_kb(args[0], args[1])
    #     return results
