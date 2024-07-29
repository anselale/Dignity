# Modules/process_slash_modules.py

import shlex
from typing import List


class SlashCommands:
    def __init__(self, memory_instance):
        self.memory = memory_instance
        self.commands = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]

    def parse(self, input):
        input_string = input.get('arg')
        args = shlex.split(input_string)
        if not args:
            return "No command provided. Type 'help' for a list of commands."

        command = args[0].lower()
        if command in self.commands:
            return getattr(self, command)(args[1:])
        else:
            return f"Unknown command: {command}. Type 'help' for a list of commands."

    def help(self, args: List[str] = None) -> str:
        if args and args[0] == '-?':
            return "help: List all available commands or get help for a specific command."

        help_text = "Available commands:\n"
        for cmd in self.commands:
            doc = getattr(self, cmd).__doc__
            help_text += f"  {cmd}: {doc.strip() if doc else 'No description available.'}\n"
        return help_text

    def echo(self, args: List[str]) -> str:
        """Repeat the given text."""
        if args and args[0] == '-?':
            return "echo: Repeat the given text. Usage: echo [text]"
        return " ".join(args)

    def add(self, args: List[str]) -> str:
        """Add two numbers."""
        if args and args[0] == '-?':
            return "add: Add two numbers. Usage: add [number1] [number2]"
        if len(args) != 2:
            return "Error: Add requires exactly two arguments."
        try:
            return str(float(args[0]) + float(args[1]))
        except ValueError:
            return "Error: Both arguments must be numbers."

    def challenge(self, args: List[str]) -> str:
        """This is where the challenge would go, if I had one"""
        if args and args[0] == '-?':
            return "This is where the challenge text would go, if I had one"
        else:
            return "This is where the challenge text would go, if I had one"
