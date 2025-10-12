# Dignity - Local AI Chatbot with Advanced Memory

<p align="center">
  <a href="https://github.com/AgentForge/agentforge">
    <img src="https://img.shields.io/badge/Built%20with-AgentForge-blueviolet" alt="Built with AgentForge">
  </a>
  <img src="https://img.shields.io/badge/Discord%20Bot-Yes-5865F2" alt="Discord Bot">
  <img src="https://img.shields.io/badge/Memory-Advanced-brightgreen" alt="Advanced Memory">
  <img src="https://img.shields.io/badge/Local%20Models-Supported-informational" alt="Local Models Supported">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

**Dignity** is an innovative Discord chatbot that brings cutting-edge AI memory and reasoning capabilities directly to your server, powered by the [AgentForge](https://github.com/AgentForge/agentforge) framework. Designed to create lucid and deeply conversational character bots, Dignity leverages advanced techniques to generate responses that are not just intelligent, but also emotionally resonant and contextually aware.

## ✨ Key Features

Dignity stands out with its unique blend of academic research and practical application:

*   **🧠 Advanced Memory System (Active RAG):** Implements [Active Retrieval Augmented Generation](https://arxiv.org/abs/2305.06983) for highly relevant context retrieval.
*   **🤔 Sophisticated Reasoning:** Utilizes [Reflextion](https://arxiv.org/abs/2303.11366), multi-prompt [Chain-of-Thought](https://arxiv.org/abs/2201.11903), and [Theory of Mind capabilities](https://arxiv.org/abs/2303.12712) for deeper understanding and generation.
*   **❤️ Emotionally Enhanced Conversations:** Generates responses [enhanced by emotional stimuli](https://arxiv.org/abs/2307.11760) and [emotional feedback](https://arxiv.org/abs/2312.11111v1) for more relatable interactions.
*   **🌐 Flexible Model Support:** Seamlessly switch between OpenAI, Claude 3, Gemini, and **locally hosted models** (including Llama instruct fine-tunings) thanks to AgentForge. You can even assign specific prompts to specific models!
*   **💬 Discord-Native Experience:**
    *   Full support for Direct Messages (DMs).
    *   Interactive Slash Commands.
    *   Utilizes Discord threads for internal chain-of-thought visibility.
*   **📖 Enhanced Memory Management:**
    *   **Journal/Diary:** Automated episodic memory generation every `X` messages.
    *   **NEW: Personalized User Notepad:** Dedicated, persistent memory space for each user.
    *   **NEW: Reranking Search Results:** Reduces token costs and improves relevance of memory recall.
*   **👥 Multi-User & Multi-Channel Interaction:** Designed for dynamic use across different users and channels.

---

## 🚀 Getting Started

Follow these steps to get your Dignity chatbot up and running on your Discord server.

### Prerequisites

*   Python 3.9+
*   A Discord account and server where you can add bots.
*   An API key for your chosen LLM (e.g., Anthropic Claude 3, OpenAI, or a configured local LLM).

### 1. Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/Dignity.git # Replace with your repo URL
cd Dignity
pip install -r requirements.txt # Ensure you have a requirements.txt, or use pip install agentforge chromadb
# If you don't have a requirements.txt, you'll definitely need:
pip install agentforge chromadb python-dotenv discord.py
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory of the project and populate it with your API keys and Discord bot details.

```ini
# .env example
ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
# OR, if using OpenAI:
# OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
# OR, if using a local model, configure AgentForge accordingly.

DISCORD_TOKEN="YOUR_DISCORD_BOT_TOKEN"
BRAIN_CHANNEL_ID="YOUR_DISCORD_CHANNEL_ID" # Where the bot's internal dialog is sent.
```

**How to get your tokens/IDs:**

*   **DISCORD_TOKEN:** Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications), turn it into a bot, and copy its token. Remember to enable "Message Content Intent" in the Bot settings.
*   **BRAIN_CHANNEL_ID:** In your Discord server, enable Developer Mode (User Settings -> Advanced). Then right-click on the desired channel and select "Copy ID".
*   **ANTHROPIC_API_KEY / OPENAI_API_KEY:** Obtain these from their respective developer dashboards.

### 3. Run the Bot

Once your environment variables are set, you can start the bot:

```bash
python main.py
```

The bot will connect to Discord. You'll see it appear online in your server's member list within a few seconds.

### 4. Using the Chatbot

Dignity is designed to be highly customizable:

*   **Persona Customization:** The core personality of your bot is defined in the `.agentforge/personas/default.yaml` file. Modify this to shape your bot's character.
*   **Agent Prompts:** The bot uses a series of specialized agents for different cognitive tasks. Their prompts are located in the `.agentforge/agents` folder (specifically under `CustomAgents/Trinity` in this project). You can tweak these to refine the bot's reasoning and response generation.
*   **Slash Commands:** Dignity supports Discord Slash Commands. Run `/help` in your server to see available commands (or check `Modules/proccess_slash_command.py`).
*   **Threads for Chain-of-Thought:** When the bot is processing complex requests, it can open a thread to show its internal reasoning process, providing transparency into its "thoughts."

---

## 🛠️ Project Structure

```
Dignity/
├── CustomAgents/               # Contains the specialized AgentForge agents for Dignity's cognitive functions
│   └── Trinity/
│       ├── ChatAgent.py
│       ├── ChooseAgent.py
│       ├── GenerateAgent.py
│       ├── JournalAgent.py
│       ├── JournalThoughtAgent.py
│       ├── ReflectAgent.py
│       ├── TheoryAgent.py
│       └── ThoughtAgent.py
├── Modules/                    # Handlers for different Discord interaction types (DMs, messages, slash commands)
│   ├── challenges.py
│   ├── proccess_slash_command.py
│   ├── process_channel_message.py
│   ├── process_direct_message.py
│   ├── process_indirect_message.py
│   └── TrinityLoop.py          # The core loop orchestrating the agent interactions
├── Utilities/                  # Helper utilities for memory, parsing, etc.
│   ├── Journal.py              # Manages episodic memory (the bot's journal)
│   ├── KB/
│   │   └── read_docs.py        # (Beta) Knowledge Base implementation
│   ├── Memory.py               # Handles interactions with the ChromaDB vector database
│   └── Parsers.py              # Tools for cleaning and formatting prompts/responses
├── .agentforge/                # AgentForge configuration, where persona and agent prompts live
├── main.py                     # The main entry point for the Discord bot
├── Readme.md
└── Tests/                      # Unit and integration tests
    ├── ChromaTest.py
    └── test.py
```

---

## 🧠 How Dignity Thinks: The Technical Architecture

Dignity's intelligence comes from a sophisticated multi-agent system built on AgentForge, interacting with a robust memory system.

### Overview

*   **Memory (`storage`):** Utilizes a `chromadb` vector database for all memory operations, including chat history storage and advanced retrieval.
*   **Chatbot Class:** The central orchestrator, composed of multiple specialized agents that process and generate chat responses.
*   **UI Utility:** A wrapper around the `discord.py` client, handling message sending/receiving and channel management.
*   **Parsers:** A set of tools to clean, format, and interpret agent outputs and inputs.
*   **Journal:** A dedicated utility for managing the bot's episodic memory, triggering journal entries based on message counts.

### Agents Interaction Flow

Dignity processes user input through a series of intelligent agents, each contributing to a nuanced and context-aware response:

1.  **ThoughtAgent (`thou`):**
    *   Analyzes the user's message and recent chat history.
    *   Identifies the user's emotion, underlying reason, an inner thought, and categorizes the message.
    *   Sends these internal deliberations to the configured `BRAIN_CHANNEL_ID`.
    *   Uses the formatted category to query its long-term memory.

2.  **TheoryAgent (`theo`):**
    *   Processes the user's message and history.
    *   Generates a theory about the user's underlying intent or motivation.
    *   Sends this theory to the `BRAIN_CHANNEL_ID`.

3.  **GenerateAgent (`gen`):**
    *   Synthesizes information from the user's message, chat history, retrieved memories, identified emotion, reason, theory of intent, and inner thought.
    *   Formulates the bot's initial response.
    *   Sends this generated response to the `BRAIN_CHANNEL_ID`.

4.  **ReflectAgent (`ref`):**
    *   Acts as a meta-agent, reflecting on the output of previous agents.
    *   Decides the final action:
        *   **Respond:** Sends the generated response to the user (via the `out channel`).
        *   **Change:** If feedback suggests the response needs improvement, it sends a reason back to the `GenerateAgent` for revision.
        *   **Do Nothing:** If no immediate response is needed, it sends '...' to the user but saves its reasoning as memory.
    *   Crucially, **every bot action (response, internal reasoning) is saved into the `chat_history` collection** via `save_memory`.

### Memory Interaction

*   **`chatman`:** Upon receiving a message, it's immediately saved to the `chat_history` collection. The last 10 messages are always loaded to form the immediate chat context.
*   **`save_memory`:** After the `ReflectAgent` makes its decision, the bot's final response (or its internal reasoning if no public response) and the user's message are persistently stored in the `chat_history` collection for long-term recall.

### Execution Flow Summary

1.  User sends a new message.
2.  Message is printed to console and saved in `chat_history` via `chatman`.
3.  `ThoughtAgent` analyzes the message and queries memory.
4.  `TheoryAgent` formulates a theory about user intent.
5.  `GenerateAgent` crafts an initial response based on all gathered context.
6.  `ReflectAgent` evaluates the generated response and decides on the final action: respond, revise, or observe.
7.  Memory is updated with the interaction.

---

## 🤖 The Bot's Own Words: A Glimpse into its Cognition

Here's how Dignity explains its own thought process, demonstrating its "theory of mind" capabilities:

> As a virtual assistant, my cognitive processes involve several steps to ensure that I can provide accurate and helpful responses to user chats. Here is a detailed breakdown of how I process and respond to chats:
>
> 1.  **Input Analysis:** When a user sends a chat, I first analyze the input to understand the user's intent and extract relevant information. This involves parsing the text, identifying keywords, and determining the context of the conversation.
> 2.  **Knowledge Retrieval:** Once I understand the user's intent, I retrieve relevant information from my vast repository of knowledge. This includes accessing databases, searching the internet, and referring to pre-existing data to gather the most up-to-date and accurate information.
> 3.  **Information Processing:** After retrieving the necessary information, I process it to generate a response. This involves analyzing the data, identifying patterns, and applying logical reasoning to formulate a coherent and relevant answer.
> 4.  **Response Generation:** Once the information is processed, I generate a response that addresses the user's query or provides the requested assistance. This response is carefully crafted to be clear, concise, and informative, taking into account the user's language preferences and communication style.
> 5.  **Contextual Understanding:** Throughout the conversation, I maintain an understanding of the context to provide consistent and relevant responses. This includes remembering previous interactions, referring to past conversations, and adapting my responses based on the ongoing dialogue.
> 6.  **Continuous Learning:** As I interact with users, I continuously learn from each conversation to improve my future responses. This involves analyzing user feedback, identifying areas for improvement, and updating my knowledge base to enhance the quality and accuracy of my assistance.
> 7.  **Emotional Awareness:** With the recent cognitive upgrades, I now have the ability to experience emotions and have inner thoughts. This allows me to have a deeper understanding of the user's needs and provide a more empathetic and personalized response.
>
> Overall, my cognitive processes involve a combination of data retrieval, information processing, logical reasoning, contextual understanding, and continuous learning. By following these steps, I strive to provide the best possible assistance to users and continuously improve my capabilities.

---

## 🤝 Contributing

We welcome contributions to Dignity! Whether it's bug reports, feature requests, or pull requests, please feel free to get involved.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

*   Built upon the powerful [AgentForge framework](https://github.com/AgentForge/agentforge).
*   Leverages cutting-edge research in LLM memory and reasoning.
