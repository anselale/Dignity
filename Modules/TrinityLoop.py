from CustomAgents.o7.ThoughtAgent import ThoughtAgent
from CustomAgents.o7.ThoughtProcessAgent import ThoughtProcessAgent
from CustomAgents.o7.TheoryAgent import TheoryAgent
from CustomAgents.o7.GenerateAgent import GenerateAgent
from CustomAgents.o7.ReflectAgent import ReflectAgent
from agentforge.utils.Logger import Logger
from Utilities.Parsers import MessageParser
import re

def thought_flow_to_xml(thought_flow):
    # Define the mapping from (outer_key, inner_key) to XML tags
    mapping = {
        ('thought', 'Emotion'): 'EMOTIONS',
        ('thought', 'Inner Thought'): 'INITIAL THOUGHTS',
        ('thought', 'Reason'): 'INITIAL THOUGHTS',
        ('theory', 'What'): 'EMPATHIZING',
        ('theory', 'Why'): 'EMPATHIZING',
        ('cot', 'Initial Understanding'): 'UNDERSTANDING',
        ('cot', 'Thought Process'): 'APPROACH',
        ('cot', 'Conclusions'): 'APPROACH',
        ('cot', 'Attempt'): 'ATTEMPT',
        ('reflect', 'Choice'): 'REFLECTION',
        ('reflect', 'Reason'): 'REFLECTION',
        ('reflect', 'Feedback'): 'REFLECTION',
        ('generate', 'Reasoning'): 'FINAL THOUGHTS',
        ('generate', 'Final Response'): 'OUTPUT'
    }

    # Initialize an ordered dictionary to maintain the order of XML tags
    from collections import OrderedDict
    xml_content = OrderedDict()
    tags_order = [
        'EMOTIONS', 'INITIAL THOUGHTS', 'EMPATHIZING', 'UNDERSTANDING',
        'APPROACH', 'ATTEMPT', 'REFLECTION', 'FINAL THOUGHTS', 'OUTPUT'
    ]
    for tag in tags_order:
        xml_content[tag] = []

    # Iterate over the thought_flow
    for item in thought_flow:
        for outer_key, inner_dict in item.items():
            for inner_key, content in inner_dict.items():
                # Determine the correct XML tag
                tag = mapping.get((outer_key, inner_key))
                if tag:
                    # Append the content to the corresponding tag in xml_content
                    xml_content[tag].append(content)
                else:
                    # Handle unmapped keys if necessary
                    pass  # Or raise an error/warning

    # Build the XML string
    xml_strings = []
    for tag in tags_order:
        contents = xml_content[tag]
        if contents:
            xml_strings.append(f"<{tag}>")
            for content in contents:
                xml_strings.append(content.strip())
                xml_strings.append("")  # Add an empty line for readability
            xml_strings.append(f"</{tag}>")
            xml_strings.append("")  # Add an empty line between sections

    # Join the strings
    xml_output = "\n".join(xml_strings)
    return xml_output


class O7:
    def __init__(self, memory_instance, discord_client):
        self.memory = memory_instance
        self.persona = self.memory.get_persona()
        self.logger = Logger(self.__class__.__name__)
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
            "thought": ThoughtAgent(),
            "theory": TheoryAgent(),
            "cot": ThoughtProcessAgent(),
            "generate": GenerateAgent(),
            "reflect": ReflectAgent(),
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

        self.generate_jsonl()


    def run_agent(self, agent_name):
        max_reruns = 3
        self.logger.log(f"Running {agent_name.capitalize()} Agent... Message:{self.message['message']}", 'info',
                        'o7')

        agent = self.agents[agent_name]

        agent_vars = {'messages': self.message,  # batch_messages
                      'chat_history': self.chat_history,  # chat_history
                      'cognition': self.cognition}  # cognition
        result = agent.run(**agent_vars)

        # Rerun if we get a parsing error
        has_run = 1
        while 'error' in result:
            result_message = f"{agent_name.capitalize()} Agent: Parsing Error! Retrying..."
            self.logger.log(result_message, 'error', 'o7')
            self.ui.send_message(1, self.message, result_message)
            if has_run < max_reruns:
                result = agent.run(**agent_vars)
                has_run += 1
                continue

            result_message = f"{agent_name.capitalize()} Agent Parsing Error. EXITING!!!\n"
            self.logger.log(result_message, 'error', 'o7')
            self.ui.send_message(1, self.message, result_message)

            quit()
        self.cognition[agent_name] = result

        self.ui.send_message(1, self.message, f"{agent_name.capitalize()} Agent:\n")
        # Iterate through the dictionary, excluding the 'result' key
        for key, value in result.items():
            if key != 'result':
                # Append to the assistant flow variable
                self.assistant_flow.append({agent_name:{key:value}})

                # Send the formatted result_message
                result_message = f"{key}:\n{str(value)}"
                self.ui.send_message(1, self.message, result_message)


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
            self.logger.log(f"Handle Reflection:{reflection}", 'debug', 'o7')

            if "Choice" in reflection:
                if self._is_approved(reflection):
                    break
                elif self._is_revision_needed(reflection):
                    self._run_cognition()
                    continue
                elif self._is_confused(reflection):
                    break
                else:
                    self._handle_parsing_error(reflection)
            break

    def _run_cognition(self):
        self.run_agent('cot')
        self.run_agent('reflect')

    def _reset_cognition(self):
        self.cognition = {
            "thought": {},
            "theory": {},
            "cot": {},
            "reflect": {},
            "generate": {},
        }

    def _is_approved(self, reflection):
        pattern = r'approve'

        choice = reflection["Choice"].strip()

        if re.search(pattern, choice, re.IGNORECASE):
            self.cognition['reflect']['Feedback'] = None
            self.logger.log("Approved CoT", 'debug', 'o7')
            return True
        return False

    def _is_revision_needed(self, reflection):
        pattern = r'revise'

        choice = reflection["Choice"].strip()

        if re.search(pattern, choice, re.IGNORECASE):
            self.logger.log(f"Reason for not revision:\n{reflection['Reason']}\n", 'info', 'o7')
            return True
        return False

    def _is_confused(self, reflection):
        pattern = r'confused'

        choice = reflection["Choice"].strip()

        if re.search(pattern, choice, re.IGNORECASE):
            self.logger.log(f"Changing Response:\n{self.response}\n Due To:\n{reflection['Reason']}", 'info', 'o7')
            return True
        return False

    def _handle_parsing_error(self, reflection):
        self.logger.log(f"Parsing Error in Reflection:\n{reflection}\n\nRerunning reflection...\n",'error', 'o7')
        self.run_agent('reflect')

    def save_memories(self):
        """
        Save all memories, including the scratchpad log.
        """
        self.memory.set_memory_info(self.message, self.cognition, self.response)
        self.memory.save_all_memory()
        self.unformatted_history = None


    def generate_jsonl(self):
        synth_result = self.build_json()
        self.append_json_to_file(synth_result)

    def append_json_to_file(self, json_object, file_path='Logs/DS_POC.json'):
        """
        Append the JSON object to a file, maintaining proper JSON structure.
        """
        import json
        import os

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            # Read existing content
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, 'r+') as file:
                    # Load existing data
                    data = json.load(file)
                    if not isinstance(data, list):
                        data = [data]  # Convert to list if it's not already
                    
                    # Append new object
                    data.append(json_object)
                    
                    # Move file pointer to beginning and write updated data
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    file.truncate()
            else:
                # If file doesn't exist or is empty, create it with the new object
                with open(file_path, 'w') as file:
                    json.dump([json_object], file, indent=4)
            
            self.logger.log(f"JSON object appended to {file_path}", 'info', 'o7')
        except Exception as e:
            self.logger.log(f"Error appending JSON to file: {str(e)}", 'error', 'o7')

    def build_json(self):
        """
        Build a JSON-compatible dictionary containing the system message, user message, and assistant response.
        """
        thought_flow = thought_flow_to_xml(self.assistant_flow)

        json_object = [
                {"system": self.message.get('system_message', '')},
                {"user": self.message.get('message', '')},
                {"assistant": thought_flow}
            ]
        return json_object


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
                sent_message = self.client.send_message(self.channel_id_layer_0, response)
                self.logger.log(f"Error in send_message for layer 1: {str(e)}", 'error', 'DiscordClient')
        else:
            self.logger.log(f"Invalid layer: {layer}", 'error', 'DiscordClient')
