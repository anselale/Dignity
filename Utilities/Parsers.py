import re
from typing import Dict
from agentforge.utils.logger import Logger

logger = Logger(__name__)


class MessageParser:

    @staticmethod
    def parse_lines(result):
        """
        Parses a result string into a dictionary of key-value pairs.

        Parameters:
        - result (str): The result string to parse.

        Returns:
        - dict: A dictionary containing the parsed key-value pairs.
        """
        result_dict = {}
        lines = result.strip().split('\n')
        for line in lines:
            parts = line.split(':', 1)  # Only split on the first colon
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                result_dict[key] = value
        return result_dict

    @staticmethod
    def format_string(input_str):
        logger.log(f"Formatting string:\n{input_str}", 'debug', 'Formatting')
        """
        Formats a string by enforcing specific rules (e.g., replacing certain characters).

        Parameters:
        - input_str (str): The string to format.

        Returns:
        - str: The formatted string.
        """
        # Remove leading and trailing whitespace
        input_str = input_str.strip()
        logger.log(f"Remove leading and trailing whitespace:\n{input_str}", 'debug', 'Formatting')

        # Replace non-alphanumeric, non-underscore, non-hyphen characters with underscores
        input_str = re.sub("[^a-zA-Z0-9_-]", "_", input_str)
        logger.log(f"Replacing non-alphanumeric:\n{input_str}", 'debug', 'Formatting')

        # Replace consecutive periods with a single period
        while ".." in input_str:
            input_str = input_str.replace("..", ".")
            logger.log(f"Replacing consecutive periods:\n{input_str}", 'debug', 'Formatting')

        # Ensure it's not a valid IPv4 address
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', input_str):
            input_str = "a" + input_str
            logger.log(f"Ensuring not a valid IPv4:\n{input_str}", 'debug', 'Formatting')

        # Ensure it starts and ends with an alphanumeric character
        if not input_str[0].isalnum():
            input_str = "a" + input_str[1:]
            logger.log(f"Ensure it starts with an alphanumeric character:\n{input_str}", 'debug', 'Formatting')
        if not input_str[-1].isalnum():
            input_str = input_str[:-1] + "a"
            logger.log(f"Ensure it ends with an alphanumeric character:\n{input_str}", 'debug', 'Formatting')

        # Ensure length is between 3 and 64 characters
        while len(input_str) < 3:
            input_str += input_str
            logger.log(f"Ensure length is at least 3 characters:\n{input_str}", 'debug', 'Formatting')
        if len(input_str) > 63:
            input_str = input_str[:63]
            logger.log(f"Ensure length is not more than 64 characters:\n{input_str}", 'debug', 'Formatting')

        input_str = input_str.lower()
        logger.log(f"Lower casing string:\n{input_str}", 'debug', 'Formatting')

        return input_str

    @staticmethod
    def format_messages(message):
        formatted_messages = []

        timestamp = message.get('timestamp', 'N/A')
        author = message.get('author', 'N/A')
        channel_name = message['channel'].name if 'channel' in message and hasattr(message['channel'],
                                                                                   'name') else 'N/A'
        channel_id = message.get('channel_id', 'N/A')
        message_text = message.get('message', 'N/A')

        formatted_message = (
            f"User: {author}\n"
            f"Message: \"{message_text}\"\n"
            f"Timestamp: {timestamp}\n"
        )
        formatted_messages.append(formatted_message)

        return "\n=====\n".join(formatted_messages)

    @staticmethod
    def format_user_specific_history_entries(history):
        formatted_entries = []
        for i, metadata in enumerate(history.get('metadatas', [])):
            entry_details = []
            # Start with User and Message
            entry_details.append(f"User: {metadata.get('User', 'N/A')}")
            entry_details.append(
                f"Message: {history['documents'][i] if i < len(history.get('documents', [])) else 'N/A'}")

            # Add Inner Thought and Response if available
            if 'InnerThought' in metadata:
                entry_details.append(f"Inner Thought: {metadata['InnerThought']}")
            if 'Response' in metadata:
                entry_details.append(f"Response: {metadata['Response']}")

            # Add other fields
            for key, value in metadata.items():
                if key not in ["User", "id", "isotimestamp", "unixtimestamp", "InnerThought", "Response"]:
                    entry_details.append(f"{key}: {value}")

            formatted_entries.append("\n".join(entry_details) + "\n")

        return "=====\n".join(formatted_entries).strip()

    @staticmethod
    def format_general_history_entries(history):
        formatted_entries = []
        channel = ''

        # Create a list of tuples (index, id) and sort it by id
        sorted_indices = sorted(enumerate(history.get('ids', [])), key=lambda x: x[1])

        for index, _ in sorted_indices:
            metadata = history['metadatas'][index]

            user = metadata.get('User', 'N/A')
            date = metadata.get('isotimestamp', 'N/A')
            message = history['documents'][index] if index < len(history.get('documents', [])) else 'N/A'

            # Start with User and Message
            entry_details: list = [f"Date: {date}", f"User: {user}", f"Message: {message}"]

            excluded_metadata = [
                "User", "id", "Response", "Reason", "Emotion", "InnerThought",
                "Channel", "isotimestamp", "unixtimestamp", "Categories"
            ]

            for key, value in metadata.items():
                if key not in excluded_metadata:
                    entry_details.append(f"{key}: {value}")

                if key == "Channel":
                    channel = value

            formatted_entries.append("\n".join(entry_details) + "\n")

        formatted_string = "=====\n".join(formatted_entries).strip()
        return f"Channel: {channel}\n=====\n{formatted_string}"

    @staticmethod
    def parse_kb(data):
        grouped_documents = {}

        for entry in data:
            metadatas = entry.get('metadatas', [])
            documents = entry.get('documents', [])

            for metadata, document in zip(metadatas, documents):
                position = metadata['Position']
                source = metadata['Source']
                source_clean = source.replace('\\', '/')
                if source_clean not in grouped_documents:
                    grouped_documents[source_clean] = {}
                if position not in grouped_documents[source_clean]:
                    if isinstance(document, list):
                        grouped_documents[source_clean][position] = document[0]
                    else:
                        grouped_documents[source_clean][position] = document

        for source in grouped_documents:
            grouped_documents[source] = dict(sorted(grouped_documents[source].items()))

        return grouped_documents

    @staticmethod
    def extract_updated_scratchpad(scratchpad_result: str) -> str:
        pattern = r'<updated_scratchpad>(.*?)</updated_scratchpad>'
        match = re.search(pattern, scratchpad_result, re.DOTALL)

        if match:
            return match.group(1).strip()
        else:
            return ""

    @staticmethod
    def format_journal_entries(history):
        """
        Formats chat logs for sending to the journal agent. The list is grouped by channel then ordered by ID.

        Args:
            history (dict): The history dictionary containing 'documents', 'ids', and 'metadatas'.

        Returns:
            str: Formatted general history entries.
        """
        channel_entries = {}
        excluded_metadata = ["id", "response", "reason", "unixtimestamp", "mentions"]

        # Group entries by channel
        for i, entry in enumerate(history.get('metadatas', []), start=1):
            document_id = i - 1
            document = ""
            if 'documents' in history and 0 <= document_id < len(history['documents']):
                document = history['documents'][document_id]

            entry_details = []
            if document:
                entry_details.append(f"Message: {document}")

            channel = entry.get("channel", "")
            if channel not in channel_entries:
                channel_entries[channel] = []

            for key, value in entry.items():
                if key.lower() not in excluded_metadata:
                    entry_details.append(f"{key.capitalize()}: {value}")

            channel_entries[channel].append((entry.get("id", 0), "\n".join(entry_details)))

        # Format entries grouped by channel and ordered by ID
        formatted_entries = []
        for channel, entries in channel_entries.items():
            entries.sort(key=lambda x: x[0])  # Sort by ID within each channel
            channel_formatted_entries = [entry[1] for entry in entries]
            formatted_entries.append(f"Channel: {channel}\n=====\n" + "\n=====\n".join(channel_formatted_entries))

        return "\n\n".join(formatted_entries).strip()

    @staticmethod
    def prepare_message_format(messages: dict) -> str:
        formatted_messages = []
        for index, message in enumerate(messages):
            # Add the formatted message to the list without leading newlines
            formatted_messages.append(f"ID: {index}\n"
                                      f"Date: {message['timestamp']}\n"  # Check if were formatting the timestamp
                                      f"Author: {message['author']}\n"
                                      f"Message: {message['message']}")
        # Join the messages with two newlines, putting newlines at the end instead of the beginning
        formatted_messages = "\n\n".join(formatted_messages).strip()
        logger.log(f"Formatted Messages:\n{formatted_messages}", 'debug', 'o7')
        return formatted_messages

    @staticmethod
    def parse_markdown(markdown_text: str) -> Dict[str, Dict[str, list]]:
        """
        Parses a given Markdown text into a structured dictionary.

        The function identifies titles, sections, and items in the markdown and organizes them into a nested dictionary.
        Titles are considered top-level keys, sections are nested within titles, and items are listed under sections.

        Args:
            markdown_text (str): The Markdown text to be parsed.

        Returns:
            Dict[str, Dict[str, list]]: A dictionary representing the structured content of the Markdown text.
        """
        # Initialize the dictionary to hold the entire structure
        parsed_dict = {}
        current_section = None
        current_subsection = None

        # Split the text into lines for processing
        lines = markdown_text.split('\n')

        for line in lines:
            if line.startswith('# '):  # Check if the line is a title
                title = line[2:].strip().split(': ')[-1]
                # Extract the title name
                parsed_dict[title] = {}
                current_section = title
            elif line.startswith('## '):  # Check if the line is a section name
                section_name = line[3:].strip()
                if current_section is not None:  # Make sure there's a title to attach this section to
                    parsed_dict[current_section][section_name] = []
                    current_subsection = section_name
            elif line.startswith('- '):  # Check if the line is an item
                item = line[2:].strip()
                if current_subsection is not None:  # Make sure there's a section to attach this item to
                    parsed_dict[current_section][current_subsection].append(item)

        return parsed_dict

    @staticmethod
    def parse_kb(data):
        grouped_documents = {}

        # Iterate over each entry in the response data
        for entry in data:
            metadatas = entry.get('metadatas', [])  # Use an empty list as default if 'metadatas' is missing
            documents = entry.get('documents', [])  # Use an empty list as default if 'documents' is missing

            for metadata, document in zip(metadatas, documents):
                position = metadata['Position']
                source = metadata['Source']
                # Clean the source for display
                source_clean = source.replace('\\', '/')  # Replace backslashes with forward slashes
                # Initialize the source group if not already present
                if source_clean not in grouped_documents:
                    grouped_documents[source_clean] = {}
                # Add the document with position if it doesn't already exist
                if position not in grouped_documents[source_clean]:
                    if isinstance(document, list):
                        grouped_documents[source_clean][position] = document[0]
                    else:
                        grouped_documents[source_clean][position] = document

        # Sort documents in each group by position
        for source in grouped_documents:
            grouped_documents[source] = dict(sorted(grouped_documents[source].items()))

        return grouped_documents

    @staticmethod
    def extract_updated_scratchpad(scratchpad_result: str) -> str:
        """
        Extracts the updated scratchpad content from the ScratchpadAgent's output.

        Parameters:
        - scratchpad_result (str): The full output from the ScratchpadAgent.

        Returns:
        - str: The extracted updated scratchpad content.
        """
        pattern = r'<updated_scratchpad>(.*?)</updated_scratchpad>'
        match = re.search(pattern, scratchpad_result, re.DOTALL)

        if match:
            return match.group(1).strip()
        else:
            logger.log("No updated scratchpad content found in the result.", 'warning', 'Formatting')
            return ""

    @staticmethod
    def parse_answer(text):
        start = text.find('Answer:')
        if start != -1:
            start += len('Answer:')
            end = text.find('</form>', start)
            if end != -1:
                return text[start:end].strip()
            else:
                return text[start:].strip()
        return None