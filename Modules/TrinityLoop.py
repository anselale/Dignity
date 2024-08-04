from CustomAgents.Trinity.ThoughtAgent import ThoughtAgent
from CustomAgents.Trinity.TheoryAgent import TheoryAgent
from CustomAgents.Trinity.GenerateAgent import GenerateAgent
from CustomAgents.Trinity.ReflectAgent import ReflectAgent
from agentforge.utils.functions.Logger import Logger
from Utilities.Parsers import MessageParser
import os


class Trinity:
    def __init__(self, memory_instance, discord_client):
        self.memory = memory_instance
        self.persona = self.memory.get_persona()
        self.thought = ThoughtAgent()
        self.theory = TheoryAgent()
        self.generate = GenerateAgent()
        self.reflect = ReflectAgent()
        self.logger = Logger(self.__class__.__name__)
        self.chat_history = None
        self.user_history = None
        self.dm_history = None
        self.message = None
        self.parser = MessageParser
        self.ui = UI(discord_client)
        self.response: str = ''
        # Grouping agent-related instances into a dictionary
        self.agents = {
            "thought": ThoughtAgent(),
            "theory": TheoryAgent(),
            "generate": GenerateAgent(),
            "reflect": ReflectAgent(),
        }

        self.cognition = {
            "choose": {},
            "thought": {},
            "theory": {},
            "generate": {},
            "reflect": {},
            "kb": None
        }
        pass

    def do_chat(self, message):
        self.message = message
        self.ui.channel_id_layer_0 = self.message["channel_id"]
        if self.message['channel'].startswith('Direct Message'):
            self.chat_history = self.memory.fetch_history(collection_name=message['author'], prefix='dm')
        else:
            self.chat_history = self.memory.fetch_history(collection_name=message['channel'])
        self.user_history = self.memory.fetch_history(collection_name=message['author'],
                                                      query=self.message['message'],
                                                      is_user_specific=True,
                                                      query_size=3)
        self.dm_history = self.memory.fetch_history(collection_name=message['author'],
                                                    query=self.message['message'],
                                                    is_user_specific=True,
                                                    query_size=3, prefix='dm')

        self.run_agent('thought')
        self.memory.recall_journal_entry(self.message['message'], self.cognition['thought']["Categories"], 3)
        self.memory.recall_categories(self.message['message'], self.cognition['thought']["Categories"], 3)
        self.run_agent('theory')
        # chat with docs RAG
        self.cognition['kb'] = self.memory.query_kb(message, self.cognition['theory'].get('What'))
        self.run_agent('generate')
        self.run_agent('reflect')

        self.handle_reflect_agent_decision()

        self.save_memories()
        # write journal
        journal = self.memory.check_journal()
        if journal:
            self.ui.send_message(1, self.message, journal)

    def run_agent(self, agent_name):
        self.logger.log(f"Running {agent_name.capitalize()} Agent... Message:{self.message['message']}", 'info',
                        'Trinity')

        memories = self.memory.get_current_memories()
        journals = self.memory.get_current_journals()
        agent = self.agents[agent_name]
        # agent.load_additional_data(self.messages, self.chosen_msg_index, self.chat_history,
        #                            self.user_history, memories, self.cognition)
        agent_vars = {'messages': self.message,  # batch_messages
                      'chat_history': self.chat_history,  # chat_history
                      'user_history': self.user_history,  # user_history
                      'memories': memories,  # memories
                      'journals': journals,  # journals
                      'kb': self.cognition['kb'],  # knowledgebase
                      'cognition': self.cognition}  # cognition
        self.cognition[agent_name] = agent.run(**agent_vars)

        # Send result to Brain Channel
        result_message = f"{agent_name.capitalize()} Agent:\n```{str(self.cognition[agent_name]['result'])}```"
        self.ui.send_message(1, self.message, result_message)

    def handle_reflect_agent_decision(self):
        max_iterations = 1
        iteration_count = 0

        while True:
            iteration_count += 1
            if iteration_count > max_iterations:
                self.logger.log("Maximum iteration count reached, forcing response", 'warning', 'Trinity')
                self.response = self.cognition['generate'].get('result')
                self.ui.send_message(0, self.message, self.response)
                self.cognition['reflect']['Choice'] = 'respond'
                break
            else:
                reflection = self.cognition['reflect']
                self.response = self.cognition['generate'].get('result')
                self.logger.log(f"Handle Reflection:{reflection}", 'debug', 'Trinity')

                if "Choice" in reflection:
                    if reflection["Choice"] == "respond":
                        response_log = f"Generated Response:\n{self.response}\n"
                        self.logger.log(response_log, 'debug', 'Trinity')
                        self.ui.send_message(0, self.message, self.response)
                        break

                    elif reflection["Choice"] == "nothing":
                        self.logger.log(f"Reason for not responding:\n{reflection['Reason']}\n", 'info', 'Trinity')
                        self.response = f"... (Did not respond to {self.message['author']} because {reflection['Reason']})"
                        self.ui.send_message(0, self.message, f"...")
                        return

                    elif reflection["Choice"] == "change":
                        self.logger.log(f"Changing Response:\n{self.response}\n Due To:\n{reflection['Reason']}",
                                        'info', 'Trinity')
                        self.run_agent('generate')
                        self.run_agent('reflect')
                        continue
                    else:
                        self.logger.log(f"No Choice in Reflection Response:\n{reflection}", 'error', 'Trinity')
                        self.run_agent('generate')
                        self.run_agent('reflect')
            break

    def save_memories(self):
        self.memory.set_memory_info(self.message, self.cognition, self.response)
        self.memory.save_all_memory()
        self.memory.wipe_current_memories()


class UI:
    def __init__(self, client):
        self.client = client
        self.channel_id_layer_0 = None
        self.channel_id_layer_1 = int(os.getenv('BRAIN_CHANNEL'))

    def send_message(self, layer, message, response):
        if layer == 0:

            if message['channel'].startswith('Direct Message'):
                self.client.send_dm(message['author_id'].id, response)
            else:
                channel_id = self.channel_id_layer_0

        elif layer == 1:
            channel_id = self.channel_id_layer_1
        else:
            print(f"Invalid layer: {layer}")
            return

        if channel_id:
            self.client.send_message(channel_id, response)
        else:
            print(f"Channel ID not set for layer {layer}")
