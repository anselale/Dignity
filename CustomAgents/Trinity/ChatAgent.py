from agentforge.agent import Agent
from Utilities.Parsers import MessageParser


class ChatAgent(Agent):
    parser = MessageParser

    def process_data(self):
        chat_message = self.template_data['messages']
        self.template_data['new_messages'] = self.parser.format_messages(self.template_data['messages'])
        # self.template_data['chat_history'] = chat_history
        # self.template_data['user_history'] = user_history
        self.template_data['chat_message'] = chat_message['message']
        self.template_data['username'] = chat_message['author']
        self.template_data['kb'] = self.template_data['cognition']['kb']
        self.template_data['scratchpad'] = self.template_data['cognition']['scratchpad']
        # self.template_data['formatted_mentions'] = chat_message['formatted_mentions']

        # self.template_data['memories'] = memories

        self.template_data['emotion'] = self.template_data['cognition']['thought'].get('Emotion')
        self.template_data['reason'] = self.template_data['cognition']['thought'].get('Reason')
        self.template_data['thought'] = self.template_data['cognition']['thought'].get('Inner Thought')
        self.template_data['what'] = self.template_data['cognition']['theory'].get("What", "Unknown.")
        self.template_data['why'] = self.template_data['cognition']['theory'].get("Why", "Not enough information.")
        self.template_data['response'] = self.template_data['cognition']['generate'].get('result')
        self.template_data['response_commentary'] = self.template_data['cognition']['generate'].get('OptionalReflection')
        self.template_data['choice'] = self.template_data['cognition']['reflect'].get("Choice")
        self.template_data['reflection_reason'] = self.template_data['cognition']['reflect'].get("Reason")
        self.template_data['feedback'] = self.template_data['cognition']['reflect'].get("Feedback")
        self.images = self.template_data.get('image_urls', [])

    def parse_result(self):
        self.logger.log(f"{self.agent_name} Results:\n{self.result}", 'debug', 'Trinity')
        try:
            result = str(self.result)
            self.parsed_result = self.parser.parse_lines(result)
            self.parsed_result['result'] = result
        except Exception as e:
            self.logger.parsing_error(self.parsed_result, e)

    def save_result(self):
        pass
