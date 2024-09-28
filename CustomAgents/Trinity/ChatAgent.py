from agentforge.agent import Agent
from Utilities.Parsers import MessageParser


class ChatAgent(Agent):
    parser = MessageParser

    def load_additional_data(self):
        chat_message = self.data['messages']
        self.data['new_messages'] = self.parser.format_messages(self.data['messages'])
        # self.data['chat_history'] = chat_history
        # self.data['user_history'] = user_history
        self.data['chat_message'] = chat_message['message']
        self.data['username'] = chat_message['author']
        self.data['kb'] = self.data['cognition']['kb']
        self.data['scratchpad'] = self.data['cognition']['scratchpad']
        # self.data['formatted_mentions'] = chat_message['formatted_mentions']

        # self.data['memories'] = memories

        # Thought Agent
        self.data['emotion'] = self.data['cognition']['thought'].get('Emotion')
        self.data['reason'] = self.data['cognition']['thought'].get('Reason')
        self.data['thought'] = self.data['cognition']['thought'].get('Inner Thought')

        # Theory Agent
        self.data['what'] = self.data['cognition']['theory'].get("What", "Unknown.")
        self.data['why'] = self.data['cognition']['theory'].get("Why", "Not enough information.")

        # CoT agent
        self.data['chain_of_thought'] = self.data['cognition']['cot'].get("result")

        # Reflection Agent
        self.data['choice'] = self.data['cognition']['reflect'].get("Choice")
        self.data['reflection_reason'] = self.data['cognition']['reflect'].get("Reason")
        self.data['feedback'] = self.data['cognition']['reflect'].get("Feedback")

        # Generate Agent
        self.data['response_reasoning'] = self.data['cognition']['generate'].get('Reasoning')
        self.data['response'] = self.data['cognition']['generate'].get('Response')

    def parse_result(self):
        self.logger.log(f"{self.agent_name} Results:\n{self.result}", 'debug', 'Trinity')
        try:
            result = str(self.result)
            # self.result = self.parser.parse_lines(result)
            self.result = self.functions.parsing_utils.parse_yaml_content(result)
            self.result['result'] = self.functions.parsing_utils.extract_yaml_block(result)
        except Exception as e:
            self.logger.parsing_error(self.result, e)

    def save_result(self):
        pass
