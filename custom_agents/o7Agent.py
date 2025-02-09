import re
from agentforge.agent import Agent
from agentforge.utils.parsing_processor import ParsingProcessor
from collections import OrderedDict

def parse_markdown_to_dict(markdown_text):
    parsed_dict = OrderedDict()
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

class O7Agent(Agent):
    parsing_utils = ParsingProcessor()
    parser_agent = Agent("ParsingAgent")
    max_parsing_attempts = 3  # Set the maximum number of parsing attempts
    max_generation_attempts = 3  # Set the maximum number of generation attempts

    def process_data(self):
        cognition = self.template_data['cognition']

        # Thought Agent
        self.template_data['emotion'] = cognition['thought'].get('Emotion')
        self.template_data['reason'] = cognition['thought'].get('Reason')
        self.template_data['thought'] = cognition['thought'].get('Inner Thought')

        # Theory Agent
        self.template_data['what'] = cognition['theory'].get("What", "Unknown.")
        self.template_data['why'] = cognition['theory'].get("Why", "Not enough information.")

        # Thought Process Agent
        self.template_data['chain_of_thought'] = cognition['cot'].get("result")
        self.template_data['understanding'] = cognition['cot'].get("Initial Understanding")
        self.template_data['thought_process'] = cognition['cot'].get("Thought Process")
        self.template_data['conclusions'] = cognition['cot'].get("Conclusions")

        # Reflection Agent
        self.template_data['choice'] = cognition['reflect'].get("Choice")
        self.template_data['reflection_reason'] = cognition['reflect'].get("Reason")
        self.template_data['feedback'] = cognition['reflect'].get("Feedback")

        # Generate Agent
        self.template_data['response_reasoning'] = cognition['generate'].get('Reasoning')
        self.template_data['response'] = cognition['generate'].get('Final Response')

    def parse_result(self):
        self.logger.log(f"{self.agent_name} Results:\n{self.result}", 'debug', 'o7')
        generation_attempts = 0
        max_generation_attempts = self.max_generation_attempts

        while generation_attempts < max_generation_attempts:
            result_str = str(self.result)
            parsing_attempts = 0
            max_attempts = self.max_parsing_attempts

            try:
                expected_format = self.retrieve_response_format()
                while parsing_attempts < max_attempts:
                    parsed_result = self.attempt_parsing_and_validation(result_str, expected_format)
                    if parsed_result:
                        # Parsing and validation succeeded
                        self.result = parsed_result
                        self.result['result'] = result_str
                        return
                    else:
                        parsing_attempts += 1
                        self.logger.log(f"Parsing attempt {parsing_attempts} failed.", 'info')
                        if parsing_attempts >= max_attempts:
                            break  # Break out of parsing loop to retry generation
                        else:
                            self.logger.log("Attempting to parse with ParsingAgent.", 'info')
                            # Call the ParsingAgent to attempt parsing
                            result_str = self.run_parsing_agent(result_str)

                            # Use regex to check for the invalid text pattern anywhere in the result
                            if result_str is None or re.search(r"\*\*\[INVALID TEXT: Unable to parse]\*\*",
                                                               result_str):
                                self.logger.log("ParsingAgent failed to reformat the response.", 'info')
                                break  # Break out of parsing loop to retry generation
                            # Continue the loop with the new result_str
                # After parsing attempts exhausted or failed, increment generation_attempts and rerun the LLM
                generation_attempts += 1
                if generation_attempts >= max_generation_attempts:
                    error_message = "Parsing Error: Unable to parse result into expected format after maximum generation attempts."
                    self.result = {'error': error_message}
                    return
                else:
                    self.logger.log("Re-running LLM to generate a new response.", 'info')
                    # Rerun the LLM to get a new response
                    self.run_llm()
                    # The result of LLM is stored in self.result, so we can continue
            except Exception as e:
                self.handle_parsing_error(result_str, e)
                return  # Exit after handling exception

    def attempt_parsing_and_validation(self, result_str, expected_format):
        """
        Attempts to parse the result_str and validate it against the expected_format.
        Returns the parsed result if successful, or None if unsuccessful.
        """
        parsed_result = self.parse_agent_result(result_str)
        if parsed_result is None or parsed_result is {}:
            self.logger.log("Parsing Error: Unable to parse result into dictionary.", 'error')
            return None

        # Validate the parsed result against the expected format
        if expected_format:
            validation_errors = self.compare_dict_keys(expected_format, parsed_result)
            if validation_errors:
                self.logger.log("Validation failed.", 'info')
                return None
            else:
                self.logger.log("Parsed result matches the expected format.", 'info')
                return parsed_result
        else:
            self.logger.log("No expected format to validate against.", 'warning')
            return parsed_result

    def retrieve_response_format(self):
        """
        Retrieves and parses the expected response format from agent data.
        Returns the expected format as a dictionary.
        """
        response_format_markdown = self.get_response_format_markdown()
        if response_format_markdown:
            # Extract and parse the expected format
            expected_format = parse_markdown_to_dict(response_format_markdown)
            return expected_format

        self.logger.log("No response format specified in prompts.", 'warning')
        return None

    def get_response_format_markdown(self):
        """
        Retrieves the Response Format markdown from agent data.
        Returns the markdown string or None if not found.
        """
        response_format = self.agent_data['prompts']['system'].get("Response Format")
        if not response_format:
            response_format = self.agent_data['prompts']['user'].get("Response Format")

        if response_format:
            # Extract the Markdown code block from the response format
            _ , response_format_markdown = self.parsing_utils.extract_code_block(response_format)
            return response_format_markdown

        return None

    def parse_agent_result(self, result_str):
        """
        Parses the agent's result string into a dictionary.
        Returns the parsed result dictionary.
        """
        _ , cleaned_results = self.parsing_utils.extract_code_block(result_str, '~~~')
        parsed_result = parse_markdown_to_dict(cleaned_results)
        if parsed_result is None or not isinstance(parsed_result, dict):
            self.logger.log("Parsing Error: Unable to parse result into dictionary.", 'error')
            return None
        return parsed_result

    def compare_dict_keys(self, expected, actual, path=''):
        """
        Recursively compares the keys of two dictionaries.
        Returns a list of error messages for any discrepancies found.
        """
        errors = []
        for key in expected:
            if key not in actual:
                errors.append(f"Missing key: {path + key}")
            else:
                if isinstance(expected[key], dict) and isinstance(actual[key], dict):
                    errors.extend(self.compare_dict_keys(expected[key], actual[key], path + key + '.'))
                elif isinstance(expected[key], dict) != isinstance(actual[key], dict):
                    errors.append(f"Type mismatch at key: {path + key}")
        for key in actual:
            if key not in expected:
                errors.append(f"Unexpected key: {path + key}")
        return errors

    def run_parsing_agent(self, result_str):
        """
        Calls the ParsingAgent to attempt to reformat the result into the expected format.
        Returns the new result string, or None if unsuccessful.
        """
        try:
            # Prepare the input for the ParsingAgent
            response_format_markdown = self.get_response_format_markdown()

            if not response_format_markdown:
                self.logger.log("No response format available for ParsingAgent.", 'warning')
                return None

            # Call the ParsingAgent
            parsing_agent_result = self.parser_agent.run(target_structure=response_format_markdown, text=result_str)

            # The ParsingAgent returns a corrected result string
            return parsing_agent_result

        except Exception as e:
            self.logger.log(f"Error during ParsingAgent execution: {e}", 'error')
            return None

    def handle_parsing_error(self, result_str, exception):
        """
        Handles exceptions during parsing and logs the error.
        """
        self.logger.parsing_error(result_str, exception)
        self.result = {'error': f'Exception during parsing: {str(exception)}'}

    def save_result(self):
        pass
