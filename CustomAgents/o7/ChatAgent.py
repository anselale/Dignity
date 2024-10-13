from agentforge.agent import Agent
from agentforge.utils.ParsingUtils import ParsingUtils
from Utilities.Parsers import MessageParser

def parse_markdown_to_dict(markdown_text):
    parsed_dict = {}
    current_heading = None
    content_lines = []

    lines = markdown_text.split('\n')
    for line in lines:
        # Check if the line is a heading (e.g., starts with '### ')
        if line.startswith('### '):
            # If we're already tracking content under a heading, save it
            if current_heading is not None:
                parsed_dict[current_heading] = '\n'.join(content_lines).strip()
                content_lines = []
            # Update the current heading
            current_heading = line[4:].strip()
        else:
            # If a heading has been found, collect the content
            if current_heading is not None:
                content_lines.append(line)
    # After the loop, save the content for the last heading
    if current_heading is not None:
        parsed_dict[current_heading] = '\n'.join(content_lines).strip()

    return parsed_dict

class ChatAgent(Agent):
    parser = MessageParser
    parsing_utils = ParsingUtils()

    def process_data(self):
        cognition = self.data['cognition']
        chat_message = self.data['messages']

        # Get Message Info
        self.data['username'] = chat_message['author']
        self.data['chat_message'] = chat_message['message']

        # Thought Agent
        self.data['emotion'] = cognition['thought'].get('Emotion')
        self.data['reason'] = cognition['thought'].get('Reason')
        self.data['thought'] = cognition['thought'].get('Inner Thought')

        # Theory Agent
        self.data['what'] = cognition['theory'].get("What", "Unknown.")
        self.data['why'] = cognition['theory'].get("Why", "Not enough information.")

        # Thought Process Agent
        # self.data['chain_of_thought'] = cognition['cot'].get("result")
        self.data['chain_of_thought'] = cognition['cot'].get("result")
        self.data['understanding'] = cognition['cot'].get("Initial Understanding")
        self.data['thought_process'] = cognition['cot'].get("Thought Process")
        self.data['conclusions'] = cognition['cot'].get("Conclusions")
        self.data['attempt'] = cognition['cot'].get("Attempt")

        # Reflection Agent
        self.data['choice'] = cognition['reflect'].get("Choice")
        self.data['reflection_reason'] = cognition['reflect'].get("Reason")
        self.data['feedback'] = cognition['reflect'].get("Feedback")

        # Generate Agent
        self.data['response_reasoning'] = cognition['generate'].get('Reasoning')
        self.data['response'] = cognition['generate'].get('Final Response')

    def parse_result(self):
        self.logger.log(f"{self.agent_name} Results:\n{self.result}", 'debug', 'o7')
        result = str(self.result)
        try:
            parsed_result = parse_markdown_to_dict(result)

            if parsed_result is None or not isinstance(parsed_result, dict):
                self.result = {'error': 'Parsing Error'}
                return

            self.result = parsed_result
            self.result['result'] = result
        except Exception as e:
            self.logger.parsing_error(result, e)

    # YAML Implementation
    # def parse_result(self):
    #     self.logger.log(f"{self.agent_name} Results:\n{self.result}", 'debug', 'o7')
    #     result = str(self.result)
    #     try:
    #         parsed_result = self.parsing_utils.parse_yaml_content(result)
    #
    #         if parsed_result is None or not isinstance(parsed_result, dict):
    #             self.result = {'error': 'Parsing Error'}
    #             return
    #
    #         self.result = parsed_result
    #         self.result['result'] = self.parsing_utils.extract_yaml_block(result)
    #     except Exception as e:
    #         self.logger.parsing_error(result, e)

    def save_result(self):
        pass
