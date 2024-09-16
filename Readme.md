# o7

o7 is an advanced problem-solving chatbot designed to provide expert-level assistance and guidance. Built on the [AgentForge](https://github.com/DataBassGit/AgentForge) framework, o7 employs a powerful chain of thought reasoning capability to tackle complex problems by breaking them down into logical steps and applying systematic analysis.

## Key Features

- **Chain of Thought Reasoning**: o7 applies a step-by-step logical process to analyze complex problems and develop solutions.
- **Expert Knowledge**: Leveraging a comprehensive knowledge base across multiple domains, o7 provides informed insights and recommendations.
- **Data-Driven Analysis**: Utilizing data and statistical techniques, o7 identifies patterns, trends, and correlations to inform problem-solving.
- **Scenario Planning**: o7 develops and evaluates multiple scenarios and contingencies to help users make robust decisions.
- **Explainable AI**: Providing clear and understandable explanations of its reasoning process and conclusions, o7 ensures transparency and trust.

## Architecture

o7 is built on the AgentForge framework, which enables advanced capabilities such as:

- [active retrieval augmented generation](https://arxiv.org/abs/2305.06983)
- [reflextion](https://arxiv.org/abs/2303.11366)
- multi-prompt [chain-of-thought](https://arxiv.org/abs/2201.11903)
- [theory of mind capabilities](https://arxiv.org/abs/2303.12712)
- Journal/Diary - Episodic Memory
- ***NEW*** - Personalized user notepad
- ***NEW*** - Reranking search results to reduce token costs
- *Beta* - KB implementation

These features allow o7 to generate lucid and liminal conversational interactions that are [enhanced by emotional stimuli](https://arxiv.org/abs/2307.11760). [(see also)](https://arxiv.org/abs/2312.11111v1)

## Configuration

To run o7, you will need to set up the following environment variables:

- `ANTHROPIC_API_KEY`: All prompts are optimized to run on Claude 3, but can be run against any instruct trained LLM. Instructions for other platforms can be found in the AgentForge documentation
- `DISCORD_TOKEN`: The bot needs to be registered with Discord and added to your server

You will also need to install AgentForge:

```
pip install agentforge
```

## Usage

To start o7, run:

```
python main.py
```

The bot will take a few seconds to connect to the Discord server. Once ready, you will see the bot in the members list.

## Interacting with o7

To interact with o7, simply mention the bot in a channel where the bot is present. o7 will analyze your message, apply its chain of thought reasoning, and provide a detailed response to assist you with your problem or question.

o7's persona and problem-solving skills can be customized by modifying the agent files in the `.agentforge/agents` folder and the persona prompt in the `.agentforge/personas` folder.

## Feedback and Improvement

o7 continuously learns and improves based on user feedback and interactions. If you have any suggestions or encounter any issues, please feel free to open an issue on the GitHub repository.

We hope o7 will be a valuable problem-solving companion and look forward to your feedback and contributions to make it even better.

Citations:
[1] https://github.com/DataBassGit/AgentForge