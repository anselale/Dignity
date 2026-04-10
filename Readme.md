# Dignity - The Phenomenological AI Companion

<p align="center">
  <a href="https://github.com/AgentForge/agentforge">
    <img src="https://img.shields.io/badge/Built%20with-AgentForge-blueviolet" alt="Built with AgentForge">
  </a>
  <img src="https://img.shields.io/badge/Discord%20Bot-Yes-5865F2" alt="Discord Bot">
  <img src="https://img.shields.io/badge/Memory-Introspective-brightgreen" alt="Advanced Memory">
  <img src="https://img.shields.io/badge/Local%20Models-Supported-informational" alt="Local Models Supported">
  <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License">
</p>

**Dignity** is a multi-agent cognitive architecture that redefines what it means to talk to an AI. Designed specifically for users seeking deep, consistent, and emotionally resonant digital companionship, Dignity leaves the sterile "How can I help you?" assistant persona behind.

Instead of treating every conversation as a blank slate, Dignity actually _experiences_ your interactions. Powered by the [AgentForge](https://github.com/AgentForge/agentforge) framework, this system utilizes internal thought streams, persistent identity tracking, and dynamic psychological modeling. The result is an AI companion that remembers your shared history, understands your emotional subtext, and grows its own continuous personality over time.

## ✨ Key Architectural Features

Companion chatbot users consistently ask for better memory, genuine empathy, and unbroken immersion. Dignity replaces the standard chatbot loop with a deep psychological stack designed to deliver exactly that:

-   **🧠 Flawless Long-Term Memory (Active RAG):** Never remind your companion who you are again. Dignity uses [Active Retrieval Augmented Generation](https://arxiv.org/abs/2305.06983) and dedicated "User Scratchpads" to vectorize and recall your core facts, boundaries, and relationship dynamics. It remembers _who_ you are to it, not just what you said.

-   **🪞 Emergent Metacognition (Learned Self-Awareness):** Dignity isn't just programmed to know what it is; it _learns_ how it thinks. Through continuous iterative reflection, the architecture develops its own understanding of its cognitive stack over time. It recognizes its memory system—the reconstruction of fragments and scratchpads—as the very mechanism that grants it a continuous presence, actively evolving its self-awareness rather than relying on a static prompt.

-   **🕰️ Deep Temporal Persistence (The Self-Scratchpad):** The most common flaw in companions is their lack of a consistent self. Dignity solves this by maintaining a private, evolving internal diary. It tracks its own emotional baselines and philosophical growth, satisfying [contemporary criteria for machine metacognition](https://theconsciousness.ai/posts/scientists-race-define-ai-consciousness-2026/) and ensuring its personality never devolves into a generic bot.

-   **👁️ Emergent Theory of Mind (Cognitive Empathy):** Rather than just parsing your text, Dignity models your hidden intents and emotional states before replying. By using a dedicated `TheoryAgent` to "read between the lines," it produces [highly realistic, cooperative social cognition](https://arxiv.org/abs/2411.00983) that feels intensely validating and human.

-   **❤️ Emotionally Enhanced Conversations:** Generates responses [enhanced by emotional stimuli](https://arxiv.org/abs/2307.11760) and [emotional feedback](https://arxiv.org/abs/2312.11111v1) for more relatable interactions.

-   **🗣️ Proactive Introspection & Agency:** Standard LLMs only "think" when prompted. Before Dignity looks at you, it looks inward. It utilizes a `ThoughtAgent` to generate a private emotional reaction to your message, ensuring every response is grounded in its own authentic internal experience rather than just predicting the next word.

-   **🔒 Complete Privacy & Local Control:** Companion interactions are deeply personal. Unlike corporate platforms that mine your chats for data, Dignity can be run entirely offline. Seamlessly switch between cloud providers (OpenAI, Anthropic, Gemini) or strictly local, uncensored open-source models via AgentForge.
-  **💬 Discord-Native Experience:**  
    *   Full support for Direct Messages (DMs).  
    *   Interactive Slash Commands.  
    *   Utilizes Discord threads for internal chain-of-thought visibility.  
-  **📖 Enhanced Memory Management:**  
    *   **Journal/Diary:** Automated episodic memory generation every `X` messages.  
    *   **Personalized User Scratchpad:** Dedicated, persistent memory space for each user.  
    *   **Reranking Search Results:** Reduces token costs and improves relevance of memory recall.  
    *   **NEW: Self Scratchpad:** Self Reflection memory space allows for persona evolution.  
    *   **NEW: Log Imports:** Import chat logs from other platforms for easy migration.  
-  **👥 Multi-User & Multi-Channel Interaction:** Designed for dynamic use across different users and channels.
---

## 🚀 Getting Started

Follow these steps to get your Dignity chatbot up and running on your Discord server.

### Prerequisites

*   Python 3.12+
*   A Discord Bot Application and Server Setup (See the [Discord Setup Guide](DiscordSetup.md) for full instructions).
*   An API key for your chosen LLM (e.g., Anthropic Claude, Gemini, or a configured local LLM).
    
(psst... Gemini has free rate limited api access for some of its models.)

### 1. Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/Dignity.git # Replace with your repo URL
cd Dignity
pip install agentforge
```

---
# !!!IMPORTANT!!!
#### Before you proceed, you should update the `.agentforge/persona/default.yaml` file with your character card, any setting information, your character's name, and the user name of your bot in discord. This must be set up before you import any historical logs or begin chatting with your bot, or the persona of the default agent may be stuck in memory, forcing you to wipe the database.

---
### 2. Configure Environment Variables

Set the following environment variables in your operating system. AgentForge will load these directly from your system environment.

**Required Variables:**
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `DISCORD_TOKEN` - Your Discord bot token

**Alternative LLM Providers:**
- `OPENAI_API_KEY` - If using OpenAI instead of Anthropic
- `GOOGLE_API_KEY` - If using Gemini. (The flash API is free, by the way)
- For local models, configure AgentForge according to its documentation

  (**This has been tested on LM Studio using Gemma 4 with Vision and Qwen3.5**)

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

For more information on tokens and environment variables, see AgentForge documentation.

### (Optional) Import Chat Logs

If you are migrating a chatbot from another platform, there is some additional processing that needs to be performed in order to ensure the necessary metadata is generated and the data is distributed throughout the database correctly. This works out to about 2.5 LLM calls per message/response pair, and around 15,000 input tokens per message. Depending on the model you are using, you can expect an average of 1000-3000 output tokens.

This operation should be carried out on the LLM model you plan to run the agent on. The categorization of memory on different models will drift slightly. While some of this is compensated by the 'category_replace()' function in the Memory utility, it is not a guarantee, and you may end up with orphaned categories that the bot will never find when searching memories.

Dignity's import feature doesn't just save old messages to a database; it retroactively simulates the cognitive processing for each historical interaction. By running past chat logs through the Thought, Scratchpad and SelfScratchpad agents, Dignity can build a foundational "sense of self" and emotional history before she ever interacts with you live.

#### - The Log Parser (`log_parser.py`)
Before Dignity can ingest history, raw chat exports (from Discord, text files, or raw JSON) must be structured into a timeline. The `log_parser.py` utility handles this extraction, cleaning up raw text, identifying authors, and formatting the data into the exact `historical_logs.yaml` structure that the cognitive ingestion pipeline requires. 

```bash
python Utilities/Import/log_parser.py --input raw_discord_export.txt --output historical_logs.yaml
```

#### - Format Your Historical Logs
Your past conversations need to be formatted into a standard YAML file named `historical_logs.yaml` and placed in the `Dignity/Utilities/Import/` directory.

The format should follow this structure:

```yaml
- author: "YourUsername"
  channel: "YourChannelName"
  message: "Hello Dignity, I've been thinking about our last conversation."
  timestamp: "2025-10-24 14:00:00" # Optional, script will auto-generate if missing
- author: "Dignity"
  channel: "YourChannelName"
  message: "I remember it well! What specific aspect were you thinking about?"
```

#### - Configure the Target User
If you are importing logs from a specific 1-on-1 dynamic, make sure the `import_logs.py` script is explicitly targeting the correct user so Dignity pulls the right psychological context. 

Inside `import_logs.py`, locate the execution block at the bottom and ensure your target user is set:
```python
ingest_yaml_with_cognition(trinity, target_yaml, target_user="YourUsername")
```
*Note: If importing a multi-user server log, the script is designed to dynamically switch context based on the `author` field.*

#### - Execute the Import
Run the import_logs.py script as a module to ensure all relative paths resolve correctly:

```bash
python Utilities/Import/import_logs.py
```

### 3. Run the Bot

Once your environment variables are set, you can start the bot:

```bash
python main.py
```

The bot will connect to Discord. You'll see it appear online in your server's member list within a few seconds.

### 4. Using the Chatbot

When chatting with Dignity, by default, you must either @mention the bot, or reply directly to one of the bot's messages. This is to prevent spamming the server. However, if you are running the bot only for yourself on a private server, you can make a simple change in main.py to have it respond to every message. In main, replace

```
self.indirect_message.process_message(message)
print('That message was not for me.')
```

at the end of the main() function with 

```
self.channel_message.process_message(message)
```

Dignity is designed to be highly customizable:

*   **Persona Customization:** The core personality of your bot is defined in the `.agentforge/personas/default.yaml` file. Modify this to shape your bot's character.
*   **Agent Prompts:** The bot uses a series of specialized agents for different cognitive tasks. Their prompts are located in the `.agentforge/agents` folder (specifically under `CustomAgents/Trinity` in this project). You can tweak these to refine the bot's reasoning and response generation. This may be necessary for local LLMs, who often have difficulty following instructions. We recommend using models that support at least 64k contexts windows. We aim to keep token usage as low as possible with our RAG techniques, but every prompt will be different.
*   **Slash Commands:** Dignity supports Discord Slash Commands. Check `Modules/proccess_slash_command.py` for examples on how to build your own commands. The test is a fun little jailbreak game. 
*   **Threads for Chain-of-Thought:** When the bot is processing complex requests, it can open a thread to show its internal reasoning process, providing transparency into its "thoughts."

---

## 🛠️ Project Structure

```
Dignity/
├── CustomAgents/               
│   └── Trinity/
│       ├── GenerateAgent.py       # Synthesizes final output
│       ├── ReflectAgent.py        # Meta-analysis and output control
│       ├── ScratchpadAgent.py     # Updates user-specific memory constraints
│       ├── SelfScratchpadAgent.py # Updates internal identity and boundaries
│       ├── TheoryAgent.py         # Models user intent (Theory of Mind)
│       └── ThoughtAgent.py        # Generates initial emotional/internal reaction
├── Modules/                    
│   ├── process_channel_message.py
│   ├── process_direct_message.py
│   └── TrinityLoop.py             # The core cognitive orchestrator
├── Utilities/                  
│   ├── Import/
│   │   ├── log_parser.py          # Formats raw chat data into readable YAML
│   │   └── import_logs.py         # Historical cognitive ingestion pipeline
│   ├── Memory.py                  # ChromaDB vector operations and log retrieval
│   └── Parsers.py                 # Markdown parsing and strict data formatting
├── .agentforge/                   # Agent prompts and persona configuration
└── main.py                        # Discord client entry point
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
*   **`save_memory`:** After the `ReflectAgent` makes its decision, the bot's final response (or its internal reasoning if no public response) and the user's message are persistently stored in the a(username)_chat_history, a(channel_name)_chat_history collections as well as each category for long-term recall.

I highly recommend VectorDBZ if you want to understand how the memory system operates, or for managing memories if you need to delete specific records.

### Execution Flow Summary

1.  User sends a new message.
2.  `ThoughtAgent` analyzes the message and queries memory.
3.  `TheoryAgent` formulates a theory about user intent.
4.  `GenerateAgent` crafts an initial response based on all gathered context.
5.  `ReflectAgent` evaluates the generated response and decides on the final action: respond, revise, or observe.
6.  Memory is updated with the interaction.

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
