# o7

o7 is an advanced problem-solving agent designed for researchers who want to generate, process, and validate custom Q&A fine-tuning datasets. Built on the [AgentForge](https://github.com/DataBassGit/AgentForge) framework, o7 uses a cognitive chain-of-thought approach to produce well-reasoned, step-by-step analysis. It was originally inspired by the Dignity project, but retains only the essential cognitive loop—removing Discord or other overhead—to keep things streamlined.

## Key Features

o7 supports chain-of-thought reasoning to tackle complex queries, script-based Q&A generation, and flexible configuration through **AgentForge**’s prompts and multi-agent architecture. You can easily generate datasets from a list of topics, process them with o7’s cognitive loop, validate the model’s answers, and even create a fine-tuning dataset from validated responses.

## Architecture and Inspiration

The system borrows the essential architecture from Dignity (formerly Trinity), which relies on multiple agents (e.g., **thought**, **theory**, **cot**, **reflect**, and **generate**) working in concert to produce robust reasoning. o7 removes the Discord-specific integrations found in Dignity, focusing squarely on Q&A dataset generation. You can still customize each sub-agent in `custom_agents/o7Agent.py` and update the prompts in `.agentforge/prompts` to shape the tone, style, or logic of o7.

## Installation and Configuration

After cloning or downloading the repository, make sure you have [**AgentForge**](https://github.com/DataBassGit/AgentForge) installed:

```bash
pip install agentforge
```

If you’re integrating with external LLM providers (e.g., Anthropic or HuggingFace), set environment variables (like `ANTHROPIC_API_KEY`) according to [**AgentForge**’s documentation](https://github.com/DataBassGit/AgentForge). This ensures o7 has what it needs to interact with your chosen models.

## Usage Overview

At a high level, you’ll provide a list of categories or topics (`categories.txt`), then generate Q&A pairs for each category. After that, you can aggregate all those Q&As, feed them to o7 for chain-of-thought reasoning, and finally validate o7’s answers. The main scripts to know about are:

- **`qa_generation.py`** in `qa_gen/` reads each topic from `categories.txt` and creates initial Q&A pairs in Markdown files in `qa_gen/qas`.
- **`aggregate_qas.py`** then combines those Markdown Q&A files into a single JSON (`qa_gen/qas.json`) for easier processing.
- **`process_qas_by_category.py`** reads that JSON, feeds each question to o7, and records the chain-of-thought reasoning and final answer in JSON files under `process_qas/o7responses`.
- **`aggregate_o7responses.py`** (in `process_qas/`) takes all per-category JSON files in `process_qas/o7responses` and merges them into one file, `o7responses.json`.  
- **`convert_o7responses_to_md.py`** (also in `process_qas/`) creates Markdown files from each category’s JSON, making it simple to read or share o7’s answers.
  
This sequence starts with generating raw Q&A, continues with answering them via o7, and finally aggregates everything for quick navigation. A typical pipeline might look like this:

```bash
# Step 1: Generate QA pairs from categories.
python qa_gen/qa_generation.py

# Step 2: Aggregate those QAs into a single JSON.
python qa_gen/aggregate_qas.py

# Step 3: Process them with o7’s cognitive loop.
python process_qas/process_qas_by_category.py

# (Optional) Merge individual response files into one JSON.
python process_qas/aggregate_o7responses.py

# (Optional) Convert that merged JSON to Markdown files.
python process_qas/convert_o7responses_to_md.py
```

## Validation and Fine-Tuning

In addition to generating and processing Q&A data, o7 can validate its own answers against known “gold” answers and even help you create a fine-tuning dataset.

### Validator Scripts

You’ll find the validator logic in the `validator/` folder, though there are a few key steps:

1. **`run_validator.py`** looks at the “gold” Q&A in `qa_gen/qas.json`, compares them to the corresponding answers in `process_qas/o7responses.json`, and calls a Validator Agent to produce an assessment and score for each response. Results are saved as per-category JSON files in `validator_outputs`.
2. **`aggregate_validator_outputs.py`** merges all those per-category validator outputs into a single JSON file (`validator_outputs.json`).
3. **`convert_validator_to_md.py`** creates Markdown summaries of the validator outputs, which is handy if you want a quick glance at how well o7 performed and why.

### Creating a Fine-Tuning Dataset

Once you’ve validated o7’s answers, you can generate a JSONL file for fine-tuning language models by running **`create_finetuning_dataset.py`**. This script reads each validator output, filters out low-scoring responses, and writes the remaining high-quality Q&A pairs to a JSONL file (`finetuning_dataset.jsonl`). You can then use this dataset to fine-tune your model.  
   
Here’s a brief idea of how the validation workflow might look:

```bash
# Step 1: Validate O7’s responses with a Validator Agent.
python validator/run_validator.py

# Step 2: Aggregate all validation results into one JSON.
python validator/aggregate_validator_outputs.py

# Step 3: (Optional) Convert those validation results to Markdown.
python validator/convert_validator_to_md.py

# Step 4: Create a fine-tuning dataset from the validator outputs.
python validator/create_finetuning_dataset.py
```

The scripts let you see how o7’s answers compare to ground truth, adjust your chain-of-thought reasoning prompts accordingly, and build a refined dataset for training or fine-tuning external models.

## Example: Generating and Validating a Dataset

A typical end-to-end workflow might look like this:  
1. Edit `categories.txt` and add any new topics or questions you’d like to explore.  
2. Run `qa_generation.py` to produce initial Markdown files in `qa_gen/qas`.  
3. Run `aggregate_qas.py` to combine those files into `qa_gen/qas.json`.  
4. Process the entire set via `process_qas_by_category.py`, which calls o7’s chain-of-thought logic and writes answers to `process_qas/o7responses/<category>.json`.  
5. (Optional) Merge individual category responses into `o7responses.json` using `aggregate_o7responses.py` and convert them to Markdown with `convert_o7responses_to_md.py`.  
6. Validate everything with `run_validator.py`, which produces `validator_outputs/<category>.json`.  
7. Aggregate validation results into a single file using `aggregate_validator_outputs.py`, then optionally generate Markdown summaries with `convert_validator_to_md.py`.  
8. Finally, run `create_finetuning_dataset.py` to build a JSONL file that filters out low-quality answers and keeps only responses above a configurable score threshold.

## Contributions and Feedback

We welcome any thoughts on improving o7’s reasoning capabilities, expanding the validation features, or making the Q&A generation more powerful. If you have bug reports, enhancement ideas, or code contributions, feel free to open an issue or pull request on [GitHub](https://github.com/DataBassGit/AgentForge). You can also reach out directly if you have any questions or need guidance.

We hope o7 provides a streamlined, flexible system for generating and refining Q&A datasets with step-by-step reasoning. Happy exploring—and hacking on—this cognitive agent!

---

**References**  
[1] [AgentForge on GitHub](https://github.com/DataBassGit/AgentForge)  
[2] [Chain-of-Thought Paper](https://arxiv.org/abs/2201.11903)  
[3] [Reflexion Paper](https://arxiv.org/abs/2303.11366)

[//]: # (# o7)

[//]: # ()
[//]: # (o7 is an advanced problem-solving agent designed for researchers who want to generate and process custom Q&A datasets. Built on the [AgentForge]&#40;https://github.com/DataBassGit/AgentForge&#41; framework, o7 focuses on a cognitive chain-of-thought approach to produce well-reasoned, step-by-step analysis. Originally inspired by the Dignity project, o7 retains the essential cognitive loop—minus any Discord or other overhead integrations—to keep things streamlined.)

[//]: # ()
[//]: # (## Key Features)

[//]: # ()
[//]: # (- **Chain-of-Thought Reasoning**: A structured, step-by-step reasoning process that helps tackle complex questions.)

[//]: # (- **Script-Based Dataset Generation**: Easily generate Q&A pairs based on an input list of topics &#40;categories&#41;.)

[//]: # (- **Customizable Prompts**: Adjust the agent prompts in the `.agentforge/prompts` folder to shape o7’s behavior and response style.)

[//]: # (- **AgentForge Integration**: Leverages AgentForge’s flexible architecture, which allows advanced multi-agent interactions, chaining, and prompt management.)

[//]: # ()
[//]: # (## Architecture and Inspiration)

[//]: # ()
[//]: # (o7’s cognitive architecture is inspired by Dignity &#40;formerly Trinity&#41;, a multi-agent system that orchestrates different roles to generate lucid and liminal conversational character bots. In o7, we implement a similar approach with separate agents &#40;e.g., **thought**, **theory**, **cot**, **reflect**, and **generate**&#41; coordinating to produce in-depth reasoning. However, the Discord client and other overhead have been removed, resulting in a more lightweight solution tailored for dataset generation.)

[//]: # ()
[//]: # (## Installation and Configuration)

[//]: # ()
[//]: # (1. Clone or download this repository.)

[//]: # (2. Install [AgentForge]&#40;https://github.com/DataBassGit/AgentForge&#41; &#40;and any other dependencies listed in your `requirements.txt` or environment file&#41;:)

[//]: # (   ```bash)

[//]: # (   pip install agentforge)

[//]: # (   ```)

[//]: # (3. &#40;Optional&#41; If you plan to use Anthropics, HuggingFace, or other LLM providers, set the relevant environment variables &#40;e.g., `ANTHROPIC_API_KEY`&#41; according to [AgentForge’s documentation]&#40;https://github.com/DataBassGit/AgentForge&#41;.)

[//]: # ()
[//]: # (## Usage Overview)

[//]: # ()
[//]: # (The main goal of this project is to help researchers generate custom datasets, particularly Q&A pairs derived from an input list of categories, then process and enrich those QAs with o7’s chain-of-thought reasoning. Below is a summary of the key scripts:)

[//]: # ()
[//]: # (1. **`qa_generation.py`**  )

[//]: # (   Reads categories from a text file &#40;`categories.txt`&#41;, generates questions and answers using a QA Generation Agent, and writes each category's Q&A pairs to Markdown files in the `qa_gen/qas` folder.)

[//]: # ()
[//]: # (2. **`aggregate_qas.py`**  )

[//]: # (   Aggregates the Q&A markdown files from `qa_gen/qas` into a single JSON file &#40;`qas.json`&#41;, making it easier to process the entire set at once.)

[//]: # ()
[//]: # (3. **`process_qas_by_category.py`**  )

[//]: # (   Reads `qas.json` and feeds each question to o7’s cognitive loop. The resulting thought flow and final answer are stored in per-category JSON files in `process_qas/o7responses`.)

[//]: # ()
[//]: # (In a typical workflow, you would run:)

[//]: # ()
[//]: # (```bash)

[//]: # (# Step 1: Generate QA pairs from categories)

[//]: # (python qa_generation.py)

[//]: # ()
[//]: # (# Step 2: Aggregate those generated QAs into a single JSON)

[//]: # (python aggregate_qas.py)

[//]: # ()
[//]: # (# Step 3: Process the QAs with o7's cognitive loop)

[//]: # (python process_qas_by_category.py)

[//]: # (```)

[//]: # ()
[//]: # (### Customizing Your Q&A Generation and Reasoning)

[//]: # ()
[//]: # (- **Modify Prompts**:  )

[//]: # (  The system and user prompts for o7’s agents &#40;and for the QA Generation Agent&#41; are stored in `.agentforge/prompts` &#40;a hidden folder by default&#41;. Refer to [AgentForge’s documentation]&#40;https://github.com/DataBassGit/AgentForge&#41; for instructions on how to structure or update these YAML-based prompts.)

[//]: # ()
[//]: # (- **Adjusting Agents**:  )

[//]: # (  The core cognitive loop is in `o7.py`, while each specialized sub-agent &#40;thought, theory, cot, reflect, generate&#41; lives in `custom_agents/o7Agent.py`. You can adapt these to suit your exact reasoning style or domain-specific knowledge.)

[//]: # ()
[//]: # (- **Categories and Checkpointing**:  )

[//]: # (  - The category list is in `categories.txt`.  )

[//]: # (  - Checkpoints are managed by `checkpoint_manager.py`, which ensures you don’t regenerate or reprocess the same categories multiple times.  )

[//]: # ()
[//]: # (## Example: Generating a Dataset)

[//]: # ()
[//]: # (1. **Add or Edit Categories**: Open `categories.txt` and add any new topics &#40;one topic per line&#41;.  )

[//]: # (2. **Generate**: Run `qa_generation.py` to produce Markdown Q&A files for each category in `qa_gen/qas`.  )

[//]: # (3. **Aggregate**: Run `aggregate_qas.py` to combine all those Q&A markdown files into a single JSON &#40;`qa_gen/qas.json`&#41;.  )

[//]: # (4. **Process**: Run `process_qas_by_category.py` to feed each Q&A to o7, which performs chain-of-thought reasoning. The results &#40;including the “thought flow”&#41; are then stored in `process_qas/o7responses/<category>.json`.)

[//]: # ()
[//]: # (## Contributions and Feedback)

[//]: # ()
[//]: # (We welcome contributions that help enhance o7’s reasoning capabilities, add new features, or improve dataset generation. Feel free to open an issue or submit a pull request on [GitHub]&#40;https://github.com/DataBassGit/AgentForge&#41; if you have suggestions, bug reports, or ideas for enhancements. You can also reach out with questions or feedback.)

[//]: # ()
[//]: # (We hope o7 proves useful in your research endeavors, particularly if you need a flexible system for generating or refining Q&A datasets with step-by-step reasoning. Have fun exploring—and making improvements to—this cognitive agent!)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (**References**  )

[//]: # ([1] [AgentForge on GitHub]&#40;https://github.com/DataBassGit/AgentForge&#41;  )

[//]: # ([2] [Chain-of-Thought Paper]&#40;https://arxiv.org/abs/2201.11903&#41;  )

[//]: # ([3] [Reflexion Paper]&#40;https://arxiv.org/abs/2303.11366&#41;  )

[//]: # (```)