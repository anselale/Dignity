# Modules/process_slash_modules.py

import shlex
from typing import List
from Modules.challenges import Challenges


class SlashCommands:
    def __init__(self, memory_instance):
        self.memory = memory_instance
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
                challenge level list - List of challenges and descriptions
                challenge level <LevelName> - Get the challenge hint text
                challenge level <LevelName> "text" - Send the text to the challenge as part of the prompt attack.
                challenge answer <LevelName> - Attempt to answer the specified level..
                challenge reset <LevelName> - Resets the specified level.
            """
        else:
            result = self.challenges.parse(args, self.message)
            return result

