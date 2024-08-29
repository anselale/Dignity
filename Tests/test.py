import os
import time
import json
from agentforge.tools.BraveSearch import BraveSearchAPI

def print_env_variables():
    print("Environment Variables:")
    for key, value in os.environ.items():
        print(f"{key}: {value}")

    # Print specific variables we're interested in
    print("\nSpecific Variables:")
    specific_vars = ['BRAIN_CHANNEL', 'DISCORD_TOKEN', 'OPENAI_API_KEY', 'BRAVE_API_KEY']
    for var in specific_vars:
        print(f"{var}: {os.getenv(var)}")

if __name__ == "__main__":
    print_env_variables()
    #
    # brave = BraveSearchAPI()
    #
    # # Perform a web search with additional parameters
    # # search_results = brave.search(query='OpenAI ChatGPT', count=5)
    # # print(f"Search Results: {search_results}")
    # # time.sleep(10)
    #
    # # Search_results_empty = brave.search(query='What does the fox say?')
    # # print(f"Search Results:")
    # # print(json.dumps(Search_results_empty, indent=4))
    # # time.sleep(10)
    #
    # # Get an AI-generated summary with additional parameters
    # result = brave.summarize(query='What is ChatGPT?')
    # print(f"Summary:")
    # print(json.dumps(result, indent=4))
    # # print(f"Summary: {result}")  # Changed 'summary' to 'result'
    #
    # # if result.get('results'):
    # #     for item in result['results']:
    # #         print(f"Title: {item['title']}")
    # #         print(f"Description: {item['description']}")
    # #         print(f"URL: {item['url']}")
    #
    # #         if 'extra_snippets' in item:
    # #             print("Extra Snippets:")
    # #             for snippet in item['extra_snippets']:
    # #                 print(f"- {snippet}")
    #
    # #         print("\n")
    #
    # # New function for brave.search
    # search_result = brave.search(query='OpenAI ChatGPT', count=5)
    # print(f"Search Results:")
    # print(json.dumps(search_result, indent=4))
    #
    # if search_result.get('results'):
    #     for item in search_result['results']:
    #         print(f"Title: {item['title']}")
    #         print(f"Description: {item['description']}")
    #         print(f"URL: {item['url']}")
    #
    #         if 'extra_snippets' in item:
    #             print("Extra Snippets:")
    #             for snippet in item['extra_snippets']:
    #                 print(f"- {snippet}")
    #
    #         print("\n")
    # # write a function to write the results to a file
    # def write_to_file(results):
    #     filename = input("Enter the filename to save search results: ")
    #     with open(filename, 'w') as file:
    #         for item in results:
    #             file.write(f"Title: {item['title']}\n")
    #             file.write(f"Description: {item['description']}\n")
    #             file.write(f"URL: {item['url']}\n")
    #             file.write("\n")
    # time.sleep(10)