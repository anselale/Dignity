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
            "kb": None,
            "scratchpad": None
        }
        pass

    def do_chat(self, message):
        self.message = message
        self.ui.channel_id_layer_0 = self.message["channel_id"]
        self.ui.current_thread_id = None  # Reset the thread ID for each new chat

        # Send the initial response
        initial_response = "Processing your message..."
        self.ui.send_message(0, self.message, initial_response)

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
        self.cognition['scratchpad'] = self.memory.get_scratchpad(self.message['author'])
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
        
        # Save message to scratchpad log
        # self.memory.save_scratchpad_log(message['author'], message['message'])

        # check and update scratchpad if necessary
        self.logger.log(f"About to check scratchpad for {self.message['author']}", 'debug', 'Trinity')
        updated_scratchpad = self.memory.check_scratchpad(self.message['author'])
        self.logger.log(f"check_scratchpad returned: {updated_scratchpad[:100] if updated_scratchpad else None}", 'debug', 'Trinity')
        if updated_scratchpad:
            scratchpad_message = f"Updated scratchpad for {self.message['author']}:\n```\n{updated_scratchpad[:500]}...\n```"
            self.ui.send_message(1, self.message, scratchpad_message)

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
        """
        Save all memories, including the scratchpad log.
        """
        self.memory.set_memory_info(self.message, self.cognition, self.response)
        self.memory.save_all_memory()
        self.memory.wipe_current_memories()

class UI:
    def __init__(self, client):
        self.client = client
        self.channel_id_layer_0 = None
        self.current_thread_id = None
        self.last_message_id = None
        self.logger = Logger('DiscordClient')

    def send_message(self, layer, message, response):
        if layer == 0:
            try:
                if message['channel'].startswith('Direct Message'):
                    self.client.send_dm(message['author_id'], response)
                else:
                    channel_id = self.channel_id_layer_0
                    self.client.send_message(channel_id, response)
                
                self.last_message_id = message['message_id']
                self.logger.log(f"Message sent successfully. ID: {self.last_message_id}", 'info', 'DiscordClient')
                return self.last_message_id
            except Exception as e:
                self.logger.log(f"Error in send_message (layer 0): {str(e)}", 'error', 'DiscordClient')
                return None

        elif layer == 1:
            try:
                if not self.current_thread_id:
                    if not self.last_message_id:
                        self.logger.log("No message ID available to create thread", 'error', 'DiscordClient')
                        return

                    thread_name = f"Brain - {message['author'][:20]}"
                    self.logger.log(f"Attempting to create new thread: {thread_name}", 'info', 'DiscordClient')
                    self.current_thread_id = self.client.create_thread(
                        channel_id=int(self.channel_id_layer_0),
                        message_id=int(self.last_message_id),
                        name=thread_name
                    )
                    if self.current_thread_id is None:
                        self.logger.log("Failed to create thread: current_thread_id is None", 'error', 'DiscordClient')
                        return
                    self.logger.log(f"Thread created with ID: {self.current_thread_id}", 'info', 'DiscordClient')
                
                if self.current_thread_id:
                    self.logger.log(f"Replying to thread: {self.current_thread_id}", 'info', 'DiscordClient')
                    success = self.client.reply_to_thread(int(self.current_thread_id), response)
                    if success:
                        self.logger.log("Reply sent successfully", 'info', 'DiscordClient')
                    else:
                        self.logger.log("Failed to send reply to thread", 'error', 'DiscordClient')
                else:
                    self.logger.log("Failed to create or find thread for layer 1 message", 'error', 'DiscordClient')
            except Exception as e:
                self.logger.log(f"Error in send_message for layer 1: {str(e)}", 'error', 'DiscordClient')
        else:
            self.logger.log(f"Invalid layer: {layer}", 'error', 'DiscordClient')