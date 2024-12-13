from agentforge.utils.Logger import Logger
from agentforge.cogarch import CogArch
from Utilities.UI import UI
from Utilities.Parsers import MessageParser
from CustomAgents.Dignity.ChatAgent import ChatAgent


class Dignity:
    def __init__(self, memory_instance, discord_client):
        self.memory = memory_instance
        self.persona = self.memory.get_persona()
        self.logger = Logger(self.__class__.__name__, 'Dignity')
        self.chat_history = None
        self.user_history = None
        self.dm_history = None
        self.message = None
        self.unformatted_history = None
        self.unformatted_user_history = None
        self.unformatted_dm_history = None
        self.parser = MessageParser
        self.ui = UI(discord_client)
        self.response: str = ''
        self.assistant_flow = []
        self.cognition = {}

        # Grouping agent-related instances into a dictionary
        self.agents = {
            "thought": ChatAgent(agent_name='EmotionResponse'),
            "theory": ChatAgent(agent_name='TheoryOfMind'),
            "cot": ChatAgent(agent_name='ThoughtProcess'),
            "reflect": ChatAgent(agent_name='Reflection'),
            "generate": ChatAgent(agent_name='GenerateResponse'),

        }

    def do_chat(self, message):
        self._reset_cognition()
        self.message = message
        self.ui.channel_id_layer_0 = self.message["channel_id"]
        self.ui.current_thread_id = None  # Reset the thread ID for each new chat
        self.assistant_flow = []
        self.chat_history, self.unformatted_history = self.memory.fetch_history(collection_name=message['channel'])

        # Run Thought Agent
        self.run_agent('thought')

        # Run Theory Agent
        self.run_agent('theory')

        # Run Cognition Process
        self.run_cognition_process()

        # Run Generate Agent
        self.run_agent('generate')
        self.response = self.cognition['generate'].get('Final Response')
        self.ui.send_message(0, self.message, self.response)

        # Save chat history
        self.save_memories()

    def run_agent(self, agent_name):
        max_reruns = 3
        self.logger.info(f"Running {agent_name.capitalize()} Agent... Message:{self.message['message']}")

        agent = self.agents[agent_name]

        agent_vars = {
            'messages': self.message,  # batch_messages
            'chat_history': self.chat_history,  # chat_history
            'cognition': self.cognition  # cognition
        }
        result = agent.run(**agent_vars)

        # Rerun if we get a parsing error
        has_run = 1
        while 'error' in result:
            result_message = f"{agent_name.capitalize()} Agent: Parsing Error! Retrying..."
            self.logger.error(result_message)
            self.ui.send_message(1, self.message, result_message)
            if has_run < max_reruns:
                result = agent.run(**agent_vars)
                has_run += 1
                continue

            result_message = f"{agent_name.capitalize()} Agent Parsing Error. EXITING!!!\n"
            self.logger.error(result_message)
            self.ui.send_message(1, self.message, result_message)

            quit()

        self.cognition[agent_name] = result

        self.ui.send_message(1, self.message, f"{agent_name.capitalize()} Agent:\n")

        # Collect all key-value pairs from result (excluding 'result' key) into a single dictionary
        agent_output = {}
        for key, value in result.items():
            if key != 'result':
                agent_output[key] = value
                # Send the formatted result_message
                result_message = f"{key}:\n{str(value)}"
                self.ui.send_message(1, self.message, result_message)

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
                self.logger.warning("Maximum iteration count reached, forcing response")
                break

            reflection = self.cognition['reflect']
            self.logger.debug(f"Handle Reflection: {reflection}")
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
                self.logger.warning("No 'Choice' found in reflection. Handling as parsing error.")
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
                self.logger.info(value['log'])
                return value['action']

        self.logger.warning(f"Unknown choice in reflection: '{choice}'")
        return 'unknown'

    def _handle_parsing_error(self, reflection):
        self.logger.error(f"Parsing Error in Reflection: {reflection}\nRerunning reflection...")
        self.run_agent('reflect')

    def _reset_cognition(self):
        self.cognition = {
            "thought": {},
            "theory": {},
            "cot": {},
            "reflect": {},
            "generate": {},
        }

    def save_memories(self):
        """
        Save all memories, including the scratchpad log.
        """
        self.memory.set_memory_info(self.message, self.cognition, self.response)
        self.memory.save_all_memory()
        self.unformatted_history = None