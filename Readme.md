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
pip install agentforge
```

### 2. Configure Environment Variables

Set the following environment variables in your operating system. AgentForge will load these directly from your system environment.

**Required Variables:**
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `DISCORD_TOKEN` - Your Discord bot token

**Alternative LLM Providers:**
- `OPENAI_API_KEY` - If using OpenAI instead of Anthropic
- `GOOGLE_API_KEY` - If using Gemini. (The flash API is free, by the way)
- For local models, configure AgentForge according to its documentation

**Setting Environment Variables:**

**Linux/macOS:**
```
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
export DISCORD_TOKEN="YOUR_DISCORD_BOT_TOKEN"
```

**Windows (PowerShell):**
```
$env:ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
$env:DISCORD_TOKEN="YOUR_DISCORD_BOT_TOKEN"
```

**Windows (Command Prompt):**
```
set ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY
set DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

For persistent environment variables, add them to your system's environment configuration (e.g., `.bashrc`, `.zshrc`, or Windows Environment Variables settings).


**How to get your tokens/IDs:**

*   **DISCORD_TOKEN:** Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications), turn it into a bot, and copy its token. Remember to enable "Message Content Intent" in the Bot settings.
*   **ANTHROPIC_API_KEY / OPENAI_API_KEY:** Obtain these from their respective developer dashboards.

For more information on tokens and environment variables, see AgentForge documemntation.

### 3. Run the Bot

Once your environment variables are set, you can start the bot:

```bash
python main.py
```

The bot will connect to Discord. You'll see it appear online in your server's member list within a few seconds.

### 4. Using the Chatbot

Dignity is designed to be highly customizable:

*   **Persona Customization:** The core personality of your bot is defined in the `.agentforge/personas/default.yaml` file. Modify this to shape your bot's character.
*   **Agent Prompts:** The bot uses a series of specialized agents for different cognitive tasks. Their prompts are located in the `.agentforge/agents` folder (specifically under `CustomAgents/Trinity` in this project). You can tweak these to refine the bot's reasoning and response generation. This may be necessary for local LLMs, who often have difficulty following instructions. We recommend using models that support at least 64k contexts windows. We aim to keep token usage as low as possible with our RAG techniques, but every prompt will be different.
*   **Slash Commands:** Dignity supports Discord Slash Commands. Check `Modules/proccess_slash_command.py` for examples on how to build your own commands. The test is a fun little jailbreak game. 
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

1.  **ThoughtAgent:**
    *   Analyzes the user's message and recent chat history.
    *   Identifies the bot's emotion, underlying reason, an inner thought, and categorizes the message.
    *   Uses the formatted categories to query its long-term memory.

2.  **TheoryAgent:**
    *   Analyzes the user's message and history.
    *   Generates a theory about the user's underlying intent or motivation.

3.  **GenerateAgent:**
    *   Synthesizes information from the user's message, chat history, retrieved memories, identified emotion, reason, theory of intent, and inner thought.
    *   Formulates the bot's initial response.

4.  **ReflectAgent:**
    *   Acts as a meta-agent, reflecting on the output of previous agents.
    *   Decides the final action:
        *   **Respond:** Sends the generated response to the user.
        *   **Change:** If feedback suggests the response needs improvement, it sends a reason back to the `GenerateAgent` for revision.
        *   **Do Nothing:** If no immediate response is needed, it sends '...' to the user but saves its reasoning as memory.
    *   Crucially, **every bot action (response, internal reasoning) is saved into long-term memory** via `save_memory`.

### Memory Interaction

*   **`chatman`:** Upon receiving a message, it's immediately saved to the `chat_history` collection. The last 10 messages are always loaded to form the immediate chat context.
*   **`save_memory`:** After the `ReflectAgent` makes its decision, the bot's final response (or its internal reasoning if no public response) and the user's message are persistently stored in the chat_history collection as well as each categoryfor long-term recall.

### Execution Flow Summary

1.  User sends a new message.
2.  `ThoughtAgent` analyzes the message and queries memory.
3.  `TheoryAgent` formulates a theory about user intent.
4.  `GenerateAgent` crafts an initial response based on all gathered context.
5.  `ReflectAgent` evaluates the generated response and decides on the final action: respond, revise, or observe.
6.  Memory is updated with the interaction.

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

This project is licensed under the GNU GENERAL PUBLIC LICENS Version 3, - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

*   Built upon the powerful [AgentForge framework](https://github.com/databassgit/AgentGorge).
*   Leverages cutting-edge research in LLM memory and reasoning.
