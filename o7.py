from custom_agents.o7Agent import O7Agent
from agentforge.utils.logger import Logger


def thought_flow_to_xml(thought_flow):
    from collections import OrderedDict

    # Define the mapping from (outer_key, inner_key) to XML tags
    mapping = {
        ('thought', 'Emotion'): 'EMOTIONS',
        ('thought', 'Inner Thought'): 'INITIAL_THOUGHTS',
        ('thought', 'Reason'): 'INITIAL_THOUGHTS',
        ('theory', 'What'): 'EMPATHIZING',
        ('theory', 'Why'): 'EMPATHIZING',
        ('cot', 'Initial Understanding'): 'UNDERSTANDING',
        ('cot', 'Thought Process'): 'APPROACH',
        ('cot', 'Conclusions'): 'APPROACH',
        ('reflect', 'Choice'): 'REFLECTION',
        ('reflect', 'Reason'): 'REFLECTION',
        ('reflect', 'Feedback'): 'REFLECTION',
        ('generate', 'Reasoning'): 'FINAL_THOUGHTS',
        ('generate', 'Final Response'): 'OUTPUT'
    }

    # Initialize a list to collect XML lines
    xml_output_lines = []

    # Initialize variables to keep track of current tag and content
    current_tag = None
    current_contents = []

    # Process the thought_flow sequentially
    for item in thought_flow:
        for outer_key, inner_dict in item.items():
            # Ensure inner_dict is an OrderedDict
            if not isinstance(inner_dict, OrderedDict):
                inner_dict = OrderedDict(inner_dict)
            for inner_key, content in inner_dict.items():
                # Determine the correct XML tag
                tag = mapping.get((outer_key, inner_key))
                if tag:
                    content = content.strip()
                    if tag == current_tag:
                        # Same tag as before, accumulate content
                        current_contents.append(content)
                    else:
                        # New tag encountered
                        if current_tag is not None:
                            # Write the accumulated contents of the previous tag
                            xml_output_lines.append(f"<{current_tag}>")
                            xml_output_lines.append("\n\n".join(current_contents))
                            xml_output_lines.append(f"</{current_tag}>")
                            xml_output_lines.append("")  # Add an empty line for readability
                        # Start accumulating contents for the new tag
                        current_tag = tag
                        current_contents = [content]
                else:
                    # Handle unmapped keys if necessary
                    pass  # Or raise an error/warning

    # After processing all items, write the last accumulated tag
    if current_tag is not None and current_contents:
        xml_output_lines.append(f"<{current_tag}>")
        xml_output_lines.append("\n\n".join(current_contents))
        xml_output_lines.append(f"</{current_tag}>")
        xml_output_lines.append("")  # Add an empty line for readability

    # Join the XML lines into a single string
    xml_output = "\n".join(xml_output_lines)

    # Create XML File for easy viewing of flow
    # with open('thought_flow_output.xml', 'a') as file:
    #     file.write(xml_output)

    return xml_output


class O7:
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.message = None
        self.response: str = ''
        self.assistant_flow = []
        self.cognition = {}

        # Grouping agent-related instances into a dictionary
        self.agents = {
            "thought": O7Agent("ThoughtAgent"),
            "theory": O7Agent("TheoryAgent"),
            "cot": O7Agent("ThoughtProcessAgent"),
            "generate": O7Agent("GenerateAgent"),
            "reflect": O7Agent("ReflectAgent"),
        }

    def run_o7(self, message):
        self._reset_cognition()
        self.message = message

        # Run the processing chain:
        self.run_agent('thought')
        self.run_agent('theory')
        self.run_cognition_process()
        self.run_agent('generate')
        self.response = self.cognition['generate'].get('Final Response')

        return self.build_json()
        # category = self.message.get('category')
        # if category:
        #     self.generate_jsonl(category)

    def run_agent(self, agent_name):
        max_reruns = 3
        self.logger.log(f"Running {agent_name.capitalize()} Agent... Message:\n{self.message}", 'info', 'o7')

        agent = self.agents[agent_name]

        agent_vars = {
            'message': self.message,  # batch_messages
            'cognition': self.cognition  # cognition
        }
        result = agent.run(**agent_vars)

        # Rerun if we get a parsing error
        has_run = 1
        while 'error' in result:
            result_message = f"{agent_name.capitalize()} Agent: Parsing Error! Retrying..."
            self.logger.log(result_message, 'warning', 'o7')
            if has_run < max_reruns:
                result = agent.run(**agent_vars)
                has_run += 1
                continue

            result_message = f"{agent_name.capitalize()} Agent Parsing Error. EXITING!!!\n"
            self.logger.log(result_message, 'error', 'o7')
            quit()

        self.cognition[agent_name] = result

        # Collect all key-value pairs from result (excluding 'result' key) into a single dictionary
        agent_output = {}
        for key, value in result.items():
            if key != 'result':
                agent_output[key] = value
                # Send the formatted result_message
                result_message = f"{key}:\n{str(value)}"
                self.logger.log(result_message, 'info', 'o7')

        # Append the consolidated agent output to assistant_flow
        self.assistant_flow.append({agent_name: agent_output})

    def run_cognition_process(self):
        max_iterations = 2
        iteration_count = 0

        # Run initial CoT and Reflection agents
        self._run_cognition()

        while True:
            iteration_count += 1
            if iteration_count > max_iterations:
                self.logger.log("Maximum iteration count reached, forcing response", 'warning', 'o7')
                break

            reflection = self.cognition['reflect']
            self.logger.log(f"Handle Reflection: {reflection}", 'debug', 'o7')

            if "Choice" in reflection:
                action = self._determine_action(reflection)
                if action == 'approve' or action == 'clarify':
                    # Proceed to response generation
                    break
                elif action == 'revise':
                    # Revise the thought process
                    self._run_cognition()
                    continue
                elif action == 'reject':
                    # Reset the thought process
                    self.cognition['cot'] = {}
                    self._run_cognition()
                    continue
                else:
                    self._handle_parsing_error(reflection)
                    break  # Exit loop after handling parsing error
            else:
                self.logger.log("No 'Choice' found in reflection. Handling as parsing error.", 'warning', 'o7')
                self._handle_parsing_error(reflection)
                break  # Exit loop after handling parsing error

    def _run_cognition(self):
        self.run_agent('cot')
        self.run_agent('reflect')

    def _determine_action(self, reflection):
        choice = reflection["Choice"].strip().lower()
        reason = reflection.get('Reason', 'No reason provided.')

        actions = {
            'approve': {
                'action': 'approve',
                'log': "Approved thought process."
            },
            'revise': {
                'action': 'revise',
                'log': f"Revision needed due to: {reason}"
            },
            'reject': {
                'action': 'reject',
                'log': f"Thought process rejected due to: {reason}"
            },
            'clarify': {
                'action': 'clarify',
                'log': f"Clarification needed due to: {reason}"
            }
        }

        for key, value in actions.items():
            if key in choice:
                self.logger.log(value['log'], 'info', 'o7')
                return value['action']

        self.logger.log(f"Unknown choice in reflection: '{choice}'", 'warning', 'o7')
        return 'unknown'

    def _handle_parsing_error(self, reflection):
        self.logger.log(f"Parsing Error in Reflection: {reflection}\nRerunning reflection...", 'error', 'o7')
        self.run_agent('reflect')

    def _reset_cognition(self):
        self.cognition = {
            "thought": {},
            "theory": {},
            "cot": {},
            "reflect": {},
            "generate": {},
        }
        self.assistant_flow = []

    @staticmethod
    def sanitize_category(category):
        """
        Convert a category name into a filesystem-safe string.
        For example, "cs.AI Artificial Intelligence" becomes "cs_AI_Artificial_Intelligence".
        """
        return "".join(c if c.isalnum() else "_" for c in category)

    def build_json(self):
        """
        Build a JSON-compatible dictionary containing the system message, user message, and assistant response.
        """
        thought_flow = thought_flow_to_xml(self.assistant_flow)

        json_object = [
            {"system": "You are a thinking agent responsible for developing a detailed, step-by-step thought process in response to a request, problem, or conversation. Your task is to break down the situation or question into a structured reasoning process. If feedback is provided, integrate it into your thought process for refinement."},
            {"user": self.message},
            {"assistant": thought_flow}
        ]
        return json_object