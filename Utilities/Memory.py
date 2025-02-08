from agentforge.storage.chroma_storage import ChromaStorage
from agentforge.utils.logger import Logger
from Utilities.Parsers import MessageParser
from Utilities.Journal import Journal


class Memory:
    """
    Manages memory storage and retrieval for the chatbot.
    """

    def __init__(self, persona_file, persona_name):
        """
        Initialize the Memory system.

        Args:
            persona_file (str): Path to the persona file.
            persona_name (str): Name of the persona.
        """
        self.logger = Logger('Memory')
        self.memory = ChromaStorage()
        self.parser = MessageParser
        self.persona_file = persona_file
        self.persona = persona_name
        self.message_batch = None
        self.user_message = None
        self.cognition = None
        self.response = None
        self.current_memories = []
        self.current_journals = []

    def save_channel_simple(self, message):
        """
        Save a simple channel message to memory.

        Args:
            message (dict): The message to save, containing channel, message text, author, and timestamp.
        """
        channel = message.get('channel')
        message_text = message.get('message')
        author = message.get('author')
        time = message.get('timestamp')
        collection_name = f"a{channel}_chat_history"
        collection_name = self.parser.format_string(collection_name)

        collection_size = self.memory.search_metadata_min_max(collection_name, 'id', 'max')
        if collection_size is None or "target" not in collection_size:
            memory_id = ["1"]
            collection_int = 1
        else:
            memory_id = [str(collection_size["target"] + 1 if collection_size["target"] is not None else 1)]
            collection_int = collection_size["target"] + 1

        metadata = {
            "id": collection_int,
            "User": author,
            "Channel": channel,
            "Timestamp": time
        }

        self.memory.save_memory(collection_name=collection_name,
                                data=message_text,
                                ids=memory_id,
                                metadata=[metadata])
        pass

    def save_dm_simple(self, message):
        """
        Save a simple direct message to memory.

        Args:
            message (dict): The message to save, containing channel, message text, author, and timestamp.
        """
        channel = message.get('channel')
        message_text = message.get('message')
        author = message.get('author')
        time = message.get('timestamp')
        collection_name = f"dm{author}_chat_history"
        collection_name = self.parser.format_string(collection_name)

        collection_size = self.memory.search_metadata_min_max(collection_name, 'id', 'max')
        if collection_size is None or "target" not in collection_size:
            memory_id = ["1"]
            collection_int = 1
        else:
            memory_id = [str(collection_size["target"] + 1 if collection_size["target"] is not None else 1)]
            collection_int = collection_size["target"] + 1

        metadata = {
            "id": collection_int,
            "User": author,
            "Channel": channel,
            "Timestamp": time
        }

        self.memory.save_memory(collection_name=collection_name,
                                data=message_text,
                                ids=memory_id,
                                metadata=[metadata])
        pass

    def fetch_history(self, collection_name, prefix="a", query=None, is_user_specific=False, query_size: int = 20):
        """
        Fetch and parse history for users and channels.

        Args:
            collection_name (str): Channel name or username.
            prefix (str): Prefix for direct messages ('dm') or standard ('a'). Defaults to 'a'.
            query (str, optional): Search query for the history. Defaults to None for most recent.
            is_user_specific (bool): Chooses parser. True for user history, False for channel history.
            query_size (int): Number of results to fetch. Defaults to 20.

        Returns:
            str: Formatted history string.
        """
        print("fetch history started")
        collection_name = f"{prefix}{collection_name}_chat_history"
        collection_name = self.parser.format_string(collection_name)
        print(f"collection name: {collection_name}")
        self.logger.log(f"Fetch History from: {collection_name}\n", 'debug', 'Memory')

        print("checking collection size")
        collection_size = self.memory.count_collection(collection_name)
        print(f"Collection size {collection_size}")

        if collection_size == 0:
            return None, None
            # return "No Chat History Yet! This is the start of a new conversation.", "No Chat History Yet! This is the start of a new conversation."

        # Adjust the method of fetching history based on whether it's user-specific
        if is_user_specific and query:
            print("querying memory")
            history = self.memory.query_memory(collection_name=collection_name, query=query, num_results=query_size)
            formatted_history = self.parser.format_user_specific_history_entries(history)
        else:
            qsize = min(collection_size, query_size)  # Determine the number of messages to retrieve
            start_id = collection_size - qsize + 1  # Calculate the starting 'id' to get the last 'qsize' messages
            filters = {"id": {"$gte": start_id}}  # Retrieve messages with 'id' greater than or equal to 'start_id'

            history = self.memory.load_collection(collection_name=collection_name, where=filters)
            formatted_history = self.parser.format_general_history_entries(history)


        self.logger.log(f"Fetched History:\n{history}\n", 'debug', 'Memory')
        return formatted_history, history

    def get_persona(self):
        """
        Retrieve the persona file path.

        Returns:
            str: Path to the persona file.
        """
        return self.persona_file

    def save_all_memory(self):
        """
        Save all types of memories, including category, channel, bot response, user history, and scratchpad log.
        """
        self.save_category_memory()
        self.save_channel_memory()
        self.save_bot_response()
        self.save_user_history()
        self.save_scratchpad_log(self.user_message['author'], self.user_message['message'])
        self.logger.log(f"Saved all memories.", 'debug', 'Trinity')

    def set_memory_info(self, message_batch: dict, cognition: dict, response: str):
        """
        Set the current memory information for processing.

        Args:
            message_batch (dict): Batch of messages to process.
            cognition (dict): Current cognition state.
            response (str): Generated response.
        """
        self.message_batch = message_batch
        self.user_message = message_batch
        self.cognition = cognition
        self.response = response

    def save_to_collection(self, collection_name: str, chat_message: dict, response_message: str,
                                 metadata_extra=None):
        """
        Save a message to a specific collection in memory.

        Args:
            collection_name (str): Name of the collection to save to.
            chat_message (dict): The chat message to save.
            response_message (str): The response message to save.
            metadata_extra (dict, optional): Additional metadata to include.
        """
        collection_size = self.memory.search_metadata_min_max(collection_name, 'id', 'max')
        if collection_size is None or "target" not in collection_size:
            memory_id = ["1"]
            collection_int = 1
        else:
            memory_id = [str(collection_size["target"] + 1 if collection_size["target"] is not None else 1)]
            collection_int = collection_size["target"] + 1

        metadata = {
            "id": collection_int,
            "Response": response_message,
            "Emotion": self.cognition["thought"].get("Emotion"),
            "InnerThought": self.cognition["thought"].get("Inner Thought"),
            "Reason": self.cognition["reflect"].get("Reason"),
            "User": chat_message["author"],
            # "Mentions": chat_message["mentions"],
            "Channel": str(chat_message["channel"]),
            "Categories": str(self.cognition["thought"]["Categories"])
        }
        # Need to implement a last accessed metadata

        if metadata_extra:
            metadata.update(metadata_extra)

        message = [chat_message["message"]]
        self.memory.save_memory(collection_name=collection_name, data=message, ids=memory_id, metadata=[metadata])
        self.logger.log(f"\nSaved to {collection_name}\n"
                        f"Data (Message)={message}\n"
                        f"ID={memory_id}\n"
                        f"Metadata={metadata}",
                        'debug', 'Trinity')

    def save_category_memory(self):
        """
        Save memories categorized by the thought categories.
        """
        categories = self.cognition["thought"]["Categories"].split(",")
        for category in categories:
            collection_name = f"{category.strip()}"
            category_collection = self.parser.format_string(collection_name)
            self.logger.log(f"Saving Category to: {category_collection}\nMessage:\n{self.user_message}",
                            'debug', 'Memory')
            self.save_to_collection(category_collection, self.user_message, self.response)

    def save_channel_memory(self):
        """
        Save memories specific to the current channel.
        """
        collection_name = f"a{self.user_message['channel']}_chat_history"
        collection_name = self.parser.format_string(collection_name)
        # for index, message in enumerate(self.message_batch):
        message = self.user_message
        metadata_extra = {}
        bot_response = self.response
        self.logger.log(f"Saving Channel to: {collection_name}\nMessage:\n{message}", 'debug', 'Memory')
        self.save_to_collection(collection_name, message, bot_response, metadata_extra)
        self.save_to_collection('journal_log_table', message, bot_response, metadata_extra)

    def save_bot_response(self):
        """
        Save the bot's response to memory.
        """
        message = self.user_message.copy()
        message['message'] = self.response
        message['author'] = self.persona

        collection_name = f"a{message['channel']}_chat_history"
        collection_name = self.parser.format_string(collection_name)
        self.logger.log(f"Saving Bot Response to: {collection_name}\nMessage:\n{message}", 'debug', 'Memory')
        self.save_to_collection(collection_name, message, self.user_message['message'])
        self.save_to_collection('journal_log_table', message, self.user_message['message'])

    def save_user_history(self):
        """
        Save the user's message history to memory.
        """
        collection_name = f"a{self.user_message['author']}_chat_history"
        collection_name = self.parser.format_string(collection_name)
        self.logger.log(f"Saving User History to: {collection_name}\nMessage:\n{self.user_message}", 'debug', 'Memory')
        self.save_to_collection(collection_name, self.user_message, self.response)

    def get_current_memories(self):
        """
        Retrieve the current memories.

        Returns:
            str: Current memories or 'No Memories Found' if empty.
        """
        if self.current_memories:
            memories = str(self.current_memories[0])
            return memories

        return 'No Memories Found.'

    def get_current_journals(self):
        """
        Retrieve the current journal entries.

        Returns:
            str: Current journal entries or 'No Memories Found' if empty.
        """
        if self.current_journals:
            memories = str(self.current_journals[0])
            return memories

        return 'No Memories Found.'

    def recall_recent_memories(self):
        """
        Placeholder for recalling recent memories.
        """
        pass

    def recall_categories(self, message, categories, num_memories_per_category: int = 10):
        """
        Recall memories based on categories.

        Args:
            message (str): The message to use for recall.
            categories (str): Comma-separated list of categories.
            num_memories_per_category (int): Number of memories to recall per category. Defaults to 10.
        """
        self.logger.log(f"Recalling {num_memories_per_category} Memories per Category", 'debug', 'Memory')
        categories = categories.split(",")
        for category in categories:
            collection_name = f"{category.strip()}"
            category_collection = self.parser.format_string(collection_name)
            self.logger.log(f"Fetching Category: {category_collection}", 'debug', 'Memory')
            recalled_memories = self.memory.query_memory(collection_name=category_collection,
                                                          query=message,
                                                          num_results=num_memories_per_category)
            if recalled_memories:
                self.logger.log(f"Recalled Memories:\n{recalled_memories}", 'debug', 'Memory')
                memories = self.parser.format_user_specific_history_entries(recalled_memories)
                # Add recalled memories to current memories
                self.current_memories.append(memories)
                return recalled_memories

            self.logger.log(f"No Memories Recalled For Category: {category}", 'debug', 'Memory')

    def save_journal_log(self):
        """
        Save journal log entries.
        """
        collection_name = 'journal_log_table'
        for index, message in enumerate(self.message_batch):
            metadata_extra = {}
            bot_response = self.response
            self.logger.log(f"Saving Channel to: {collection_name}\nMessage:\n{message}",
                            'debug', 'Memory')
            self.save_to_collection(collection_name, message, bot_response, metadata_extra)

    def recall_journal_entry(self, message, categories, num_entries: int = 2):
        """
        Recall journal entries based on a message and categories.

        Args:
            message (str): The message to use for recall.
            categories (str): Comma-separated list of categories.
            num_entries (int): Number of entries to recall. Defaults to 2.

        Returns:
            str: Formatted string of recalled journal entries.
        """
        self.logger.log(f"Recalling {num_entries} entries from the journal", 'debug', 'Memory')
        journal_query = f"{message}\n\n Related Categories: {categories}"
        collection_name = 'journal_chunks_table'
        journal_chunks = self.memory.query_memory(
            collection_name=collection_name,
            query=journal_query,
            num_results=num_entries
        )

        # Create a dictionary to store the recalled memories
        recalled_memories = {
            'ids': [],
            'embeddings': None,
            'metadatas': [],
            'documents': []
        }

        if journal_chunks:
            self.logger.log(f"Recalled Memories:\n{journal_chunks}", 'debug', 'Memory')

            # Set the relevance threshold
            relevance_threshold = 0.65  # Adjust this value as needed

            for i in range(len(journal_chunks['ids'])):
                distance = journal_chunks['distances'][i]
                if distance >= relevance_threshold:
                    source_id = journal_chunks['metadatas'][i]['Source_ID']

                    filters = {"id": {"$eq": source_id}}

                    # Retrieve the full journal entry based on the source_id
                    full_entry = self.memory.load_collection(
                        collection_name='whole_journal_entries',
                        where=filters
                    )

                    if full_entry:
                        print(f"Full Entry: {full_entry}")
                        # Add the relevant fields to the recalled_memories dictionary
                        recalled_memories['ids'].append(full_entry['ids'][0])
                        recalled_memories['metadatas'].append(
                            {key: value for key, value in full_entry['metadatas'][0].items() if
                             key.lower() not in ['source', 'isotimestamp', 'unixtimestamp']})
                        recalled_memories['documents'].append(full_entry['documents'][0])

            print(f"Full Entries Appended: {recalled_memories}")
            memories = self.parser.format_user_specific_history_entries(recalled_memories)
            # Add recalled memories to current memories
            self.current_journals.append(memories)
            print(f"\n\nCurrent Memories:\n{self.current_memories}")
            return memories
        else:
            memories = self.parser.format_user_specific_history_entries(recalled_memories)
            return memories

    def wipe_current_memories(self):
        """
        Clear all current memories and journal entries.
        """
        self.current_memories = []
        self.current_journals = []

    def check_journal(self):
        """
        Check if it's time to write a journal entry and do so if necessary.

        Returns:
            bool or None: True if journal was written, None otherwise.
        """
        count = self.memory.count_collection('journal_log_table')
        print(count)
        if count >= 100:
            journal_function = Journal()
            print("Journal initialized")
            journal_written = journal_function.do_journal()
            if journal_written:
                print("Deleting Journal collection")
                self.memory.delete_collection('journal_log_table')
            return journal_written
        else:
            return None

    def query_kb(self, message, theory):
        """
        Query the knowledge base for relevant information.

        Args:
            message (str): The message to query against.
            theory (str): The theory to query against.

        Returns:
            str: Formatted string of relevant knowledge base entries.
        """
        message_kb = self.memory.search_storage_by_threshold(collection_name="docs", query=message, num_results=2)
        result = []

        if message_kb:
            for i, kb in enumerate(message_kb['metadatas']):
                try:
                    position = kb['Position']
                    source = kb['Source']

                    # Get the full entry using the id
                    entry_id = message_kb['ids'][i]
                    full_entry = self.memory.load_collection(collection_name="docs", where={"Position": {"$eq": position}})
                    if full_entry:
                        result.append(full_entry)

                    # Query for entries with position-1
                    where_list_prev = {"Position": {"$eq": position - 1}}
                    prev_results = self.memory.load_collection(collection_name="docs", where=where_list_prev)
                    if prev_results:
                        if prev_results['metadatas'][0]['Source'] == source:
                            result.append(prev_results)

                    # Query for entries with position+1
                    where_list_next = {"Position": {"$eq": position + 1}}
                    next_results = self.memory.load_collection(collection_name="docs", where=where_list_next)
                    if next_results:
                        if next_results['metadatas'][0]['Source'] == source:
                            result.append(next_results)
                except Exception as e:
                    self.logger.log(f"Error occurred while retrieving KB: {e}", 'error',
                                    'Memory')

        theory_kb = self.memory.search_storage_by_threshold(collection_name="docs", query=theory, num_results=2)
        print(f'Theory KB results: {theory_kb}')
        if theory_kb:
            for i, kb in enumerate(theory_kb['metadatas']):
                try:
                    position = kb['Position']
                    source = kb['Source']

                    # Get the full entry using the id
                    entry_id = theory_kb['ids'][i]
                    full_entry = self.memory.load_collection(collection_name="docs", where={"Position": {"$eq": position}})
                    if full_entry:
                        result.append(full_entry)

                    # Query for entries with position-1
                    where_list_prev = {"Position": {"$eq": position - 1}}
                    prev_results = self.memory.load_collection(collection_name="docs", where=where_list_prev)
                    if prev_results:
                        if prev_results['metadatas'][0]['Source'] == source:
                            result.append(prev_results)

                    # Query for entries with position+1
                    where_list_next = {"Position": {"$eq": position + 1}}
                    next_results = self.memory.load_collection(collection_name="docs", where=where_list_next)
                    if next_results:
                        if next_results['metadatas'][0]['Source'] == source:
                            result.append(next_results)
                except Exception as e:
                    self.logger.log(f"Error occurred while retrieving KB: {e}", 'error',
                                    'Memory')

        print(result)
        if result:
            parsed_documents = self.parser.parse_kb(result)

            final_output = ""
            for source, docs in parsed_documents.items():
                final_output += f'--- {source} ---\n'
                for position in sorted(docs.keys()):
                    document = docs[position]
                    final_output += f'{document}\n'

        else:
            final_output = "No documents found."

        return final_output

    def get_scratchpad(self, username):
        """
        Retrieve the scratchpad for a specific user.

        Args:
            username (str): The username to retrieve the scratchpad for.

        Returns:
            str: The scratchpad content or a default message if not found.
        """
        collection_name = f"scratchpad_{username}"
        collection_name = self.parser.format_string(collection_name)
        result = self.memory.load_collection(collection_name=collection_name)
        if result and result['documents']:
            return result['documents'][0]
        return "No information available yet. This scratchpad will be updated as we learn more about the user."

    def get_scratchpad_log(self, username):
        """
        Retrieve the scratchpad log for a specific user.

        Args:
            username (str): The username to retrieve the scratchpad log for.

        Returns:
            list: The scratchpad log entries as a list or an empty list if not found.
        """
        collection_name = f"scratchpad_log_{username}"
        collection_name = self.parser.format_string(collection_name)
        result = self.memory.load_collection(collection_name=collection_name)
        self.logger.log(f"Scratchpad Log: {result}", 'debug', 'Memory')
        if result and result['documents']:
            return result['documents']
        return []

    def save_scratchpad(self, username, content):
        """
        Save or update the scratchpad for a specific user.

        Args:
            username (str): The username to save the scratchpad for.
            content (str): The content to save in the scratchpad.
        """
        collection_name = f"scratchpad_{username}"
        collection_name = self.parser.format_string(collection_name)

        if not content.strip():  # If content is empty or just whitespace
            content = "No information available yet. This scratchpad will be updated as we learn more about the user."

        self.memory.save_memory(collection_name=collection_name, data=[content], ids=["1"])

    def save_scratchpad_log(self, username, content):
        """
        Save or update the scratchpad log for a specific user.

        Args:
            username (str): The username to save the scratchpad log for.
            content (str): The content to save in the scratchpad log.
        """
        collection_name = f"scratchpad_log_{username}"
        collection_name = self.parser.format_string(collection_name)

        collection_size = self.memory.count_collection(collection_name)
        memory_id = [str(collection_size + 1)]
        self.logger.log(f"Saving Scratchpad Log to: {collection_name}\nMessage:\n{content}\nID: {memory_id}", 'debug', 'Memory')
        self.memory.save_memory(collection_name=collection_name, data=[content], ids=memory_id)

    def save_to_scratchpad_log(self, username, message):
        scratchpad_log_name = f"scratchpad_log_{username}"
        scratchpad_log_name = self.parser.format_string(scratchpad_log_name)

        current_log = self.get_scratchpad_log(username)
        updated_log = f"{current_log}\n{message}" if current_log else message

        self.save_scratchpad_log(scratchpad_log_name, updated_log)
        self.logger.log(f"Saved message to scratchpad log for user: {username}", 'debug', 'Memory')

    def check_scratchpad(self, username):
        """
        Check if it's time to update the scratchpad for a specific user and do so if necessary.

        Args:
            username (str): The username to check the scratchpad for.

        Returns:
            str or None: Updated scratchpad content if updated, None otherwise.
        """
        self.logger.log(f"Checking scratchpad for user: {username}", 'debug', 'Memory')

        scratchpad_log = self.get_scratchpad_log(username)
        self.logger.log(f"Scratchpad log entries: {len(scratchpad_log)}", 'debug', 'Memory')
        for entry in scratchpad_log:
            self.logger.log(f"Scratchpad log entry: {entry}", 'debug', 'Memory')
        count = len(scratchpad_log)

        self.logger.log(f"Number of entries in scratchpad log: {count}", 'debug', 'Memory')

        if count >= 10:
            self.logger.log(f"Scratchpad log count >= 10, updating scratchpad", 'debug', 'Memory')
            from CustomAgents.Trinity.ScratchpadAgent import ScratchpadAgent
            scratchpad_agent = ScratchpadAgent()

            current_scratchpad = self.get_scratchpad(username)
            self.logger.log(f"Current scratchpad content: {current_scratchpad[:100]}...", 'debug', 'Memory')

            scratchpad_log_content = "\n".join(scratchpad_log)
            self.logger.log(f"Scratchpad log content: {scratchpad_log_content[:100]}...", 'debug', 'Memory')

            agent_vars = {
                "username": username,
                "scratchpad_log": scratchpad_log_content,
                "scratchpad": current_scratchpad
            }
            scratchpad_result = scratchpad_agent.run(**agent_vars)
            self.logger.log(f"Scratchpad agent result: {scratchpad_result[:100]}...\nVars: {agent_vars}", 'debug', 'Memory')

            updated_scratchpad = self.parser.extract_updated_scratchpad(scratchpad_result)
            self.logger.log(f"Updated scratchpad content: {updated_scratchpad[:100]}...", 'debug', 'Memory')

            self.save_scratchpad(username, updated_scratchpad)
            self.logger.log(f"Saved updated scratchpad for user: {username}", 'debug', 'Memory')

            # Clear the scratchpad log after processing
            collection_name = f"scratchpad_log_{username}"
            collection_name = self.parser.format_string(collection_name)
            self.memory.delete_collection(collection_name)
            self.logger.log(f"Cleared scratchpad log for user: {username}", 'debug', 'Memory')

            return updated_scratchpad

        self.logger.log(f"Scratchpad log count < 10, no update needed", 'debug', 'Memory')
        return None

    def combine_and_rerank(self, query_results: list, rerank_query, num_results=5):
        """
        Combine multiple query results, rerank them based on a new query, and return the top results.

        This function takes multiple query results, combines them, and then reranks the combined
        results based on a new query. It's useful for refining search results across multiple
        collections or queries.

        Args:
            query_results (list): A list of query result dictionaries, each containing 'ids',
                                'embeddings', 'documents', and 'metadatas'.
            rerank_query (str): The query string used for reranking the combined results.
            num_results (int, optional): The number of top results to return after reranking.
                                        Defaults to 5.

        Returns:
            dict: A dictionary containing the reranked results, including 'ids', 'embeddings',
                'documents', and 'metadatas' for the top results.

        Raises:
            ValueError: If query_results is empty or if reranking fails.

        Example:
            query_results = [results1, results2, results3]
            rerank_query = "specific topic"
            reranked = query_and_rerank(query_results, rerank_query, num_results=3)
        """
        
        # Combine all query results
        combined_query_results = self.memory.combine_query_results(*query_results)

        reranked_results = self.memory.rerank_results(
            query_results=combined_query_results,
            query=rerank_query,
            temp_collection_name="temp_reranking_collection",
            num_results=num_results
        )

        formatted_results = self.parser.format_user_specific_history_entries(reranked_results)

        return formatted_results
        
