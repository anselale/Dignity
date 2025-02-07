from CustomAgents.Trinity.ThoughtAgent import ThoughtAgent
from CustomAgents.Trinity.TheoryAgent import TheoryAgent
from CustomAgents.Trinity.GenerateAgent import GenerateAgent
from CustomAgents.Trinity.ReflectAgent import ReflectAgent
from agentforge.utils.logger import Logger
from Utilities.Parsers import MessageParser


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
        self.category_memory = None
        self.message = None
        self.unformatted_history = None
        self.unformatted_user_history = None
        self.unformatted_dm_history = None
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
            "scratchpad": None,
            "reranked_memories": None
        }
        self.image_urls = []  # Change to store multiple URLs
        pass

    def do_chat(self, message):
        self.message = message
        self.ui.channel_id_layer_0 = self.message["channel_id"]
        self.ui.current_thread_id = None  # Reset the thread ID for each new chat

        # Send the initial response for debugging and testing
        # initial_response = "Processing your message..."
        # self.ui.send_message(0, self.message, initial_response)

        if self.message['channel'].startswith('Direct Message'):
            self.chat_history, self.unformatted_history = self.memory.fetch_history(collection_name=message['author'], prefix='dm')
        else:
            print("Fetch Channel History")
            self.chat_history, self.unformatted_history = self.memory.fetch_history(collection_name=message['channel'])
        print("Fetch User History")
        self.user_history, self.unformatted_user_history = self.memory.fetch_history(collection_name=message['author'],
                                                      query=self.message['message'],
                                                      is_user_specific=True,
                                                      query_size=3)
        print("Fetch DM History")
        self.dm_history, self.unformatted_dm_history = self.memory.fetch_history(collection_name=message['author'],
                                                    query=self.message['message'],
                                                    is_user_specific=True,
                                                    query_size=3, prefix='dm')

        # Process image attachments
        self.image_urls = []
        if message['attachments']:
            for attachment in message['attachments']:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    self.image_urls.append(attachment.url)

        self.run_agent('thought')
        self.memory.recall_journal_entry(self.message['message'], self.cognition['thought']["Categories"], 3)
        self.category_memory = self.memory.recall_categories(self.message['message'], self.cognition['thought']["Categories"], 3)
        self.cognition['scratchpad'] = self.memory.get_scratchpad(self.message['author'])
        self.run_agent('theory')

        # chat with docs RAG
        self.cognition['kb'] = self.memory.query_kb(message, self.cognition['theory'].get('What'))
        self.run_agent('generate')
        self.run_agent('reflect')

        self.handle_reflect_agent_decision()

        self.save_memories()
        # write journal
        print("Check Journal")
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

        # Rerank implementation
        queries_list = [self.unformatted_user_history, self.unformatted_history, self.unformatted_dm_history]
        queries = []
        if queries_list:
            for result in queries_list:
                if result is not None:
                    # Create a standardized entry for each document
                    for i in range(len(result['documents'])):
                        normalized_entry = {
                            'documents': [result['documents'][i]],
                            'ids': [result['ids'][min(i, len(result['ids']) - 1)]],
                            'metadatas': [result['metadatas'][i]]
                        }
                        queries.append(normalized_entry)
            # for i in queries_list:
            #     if i is not None:
            #         queries.append(i)
        if self.category_memory is not None:
            for result in queries_list:
                if result is not None:
                    # Create a standardized entry for each document
                    for i in range(len(result['documents'])):
                        normalized_entry = {
                            'documents': [result['documents'][i]],
                            'ids': [result['ids'][min(i, len(result['ids']) - 1)]],
                            'metadatas': [result['metadatas'][i]]
                        }
                        queries.append(normalized_entry)

        # This is where the rerank happens. Needs to be adjusted to Theory agent instead
        # Should only need to run one time per loop. Currently runs each time.
        if self.cognition['thought']:
            query = self.cognition['thought']['Inner Thought']
        else:
            query = self.message['message']
        if queries is not None:
            self.cognition['reranked_memories'] = self.memory.combine_and_rerank(queries, query, 5)

        # agent.load_additional_data(self.messages, self.chosen_msg_index, self.chat_history,
        #                            self.user_history, memories, self.cognition)
        agent_vars = {
            'messages': self.message,
            'chat_history': self.chat_history,
            'memories': self.cognition['reranked_memories'],
            'journals': journals,
            'kb': self.cognition['kb'],
            'cognition': self.cognition,
            'image_urls': self.image_urls
        }
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
                if reflection["Choice"] == "change":
                    self.run_agent('generate')
                    reflection = self.cognition['reflect']
                    self.response = self.cognition['generate'].get('result')
                    self.logger.log(f"Handle Reflection:{reflection}", 'debug', 'Trinity')
                self.cognition['reflect']['Choice'] = 'respond'
                response_log = f"Generated Response:\n{self.response}\n"
                self.logger.log(response_log, 'debug', 'Trinity')
                self.ui.send_message(0, self.message, self.response)
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
        self.unformatted_dm_history = None
        self.unformatted_user_history = None
        self.unformatted_history = None


class UI:
    def __init__(self, client):
        self.client = client
        self.channel_id_layer_0 = None
        self.current_thread_id = None
        self.logger = Logger('DiscordClient')

    def send_message(self, layer, message, response):
        self.logger.log(f"send_message called with layer: {layer}", 'debug', 'DiscordClient')
        self.logger.log(f"Message: {message}", 'debug', 'DiscordClient')
        self.logger.log(f"Response: {response[:100]}...", 'debug', 'DiscordClient')

        if layer == 0:
            try:
                if message['channel'].startswith('Direct Message'):
                    self.client.send_dm(message['author_id'], response)
                else:
                    channel_id = self.channel_id_layer_0
                    self.logger.log(f"Sending message to channel: {channel_id}", 'debug', 'DiscordClient')
                    sent_message = self.client.send_message(channel_id, response)
                    if sent_message:
                        self.logger.log(f"Message sent successfully. ID: {sent_message.id}", 'info', 'DiscordClient')
                        return sent_message.id
                    else:
                        self.logger.log("Failed to send message", 'error', 'DiscordClient')
                        return None
            except Exception as e:
                self.logger.log(f"Error in send_message (layer 0): {str(e)}", 'error', 'DiscordClient')
                return None

        elif layer == 1:
            try:
                self.logger.log(f"Layer 1: Current thread ID: {self.current_thread_id}", 'debug', 'DiscordClient')
                if not self.current_thread_id:
                    thread_name = f"Brain - {message['author'][:20]}"
                    self.logger.log(f"Attempting to create new thread: {thread_name}", 'info', 'DiscordClient')
                    self.logger.log(f"Using channel_id: {self.channel_id_layer_0}, message_id: {message['message_id']}", 'debug', 'DiscordClient')
                    
                    self.current_thread_id = self.client.create_thread(
                        channel_id=int(self.channel_id_layer_0),
                        message_id=int(message['message_id']),
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
