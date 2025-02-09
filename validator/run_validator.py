#!/usr/bin/env python3
import os
import json
import re
from agentforge.agent import Agent
from checkpoint_manager import CheckpointManager


def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)


def extract_o7_answer(o7_item):
    """
    Helper function to retrieve the actual text of O7's answer from the
    entry in o7_items. This depends on your data structure.
    """
    if isinstance(o7_item, list):
        for entry in o7_item:
            if "assistant" in entry:
                return entry["assistant"]
    return ""


def parse_validation(validation_str):
    """
    Parses a validation string into an assessment and a score.

    Expected format:
      **Assessment**:

      <assessment text>

      **Score**:

      <score>

    If the format is matched, returns (assessment, score) as strings.
    Otherwise, returns (validation_str, "").
    """
    pattern = r"\*\*Assessment\*\*:\s*(.*?)\s*\*\*Score\*\*:\s*(\d+)"
    match = re.search(pattern, validation_str, re.DOTALL | re.MULTILINE)
    if match:
        assessment = match.group(1).strip()
        score = match.group(2).strip()
        return assessment, score
    else:
        return validation_str.strip(), ""


def main():
    # 1. Load the validator agent.
    validator_agent = Agent("ValidatorAgent")

    # 2. Load the Q&A data (the “gold” data) and the O7 responses.
    gold_qas_file = "../qa_gen/qas.json"
    o7_responses_file = "../process_qas/o7responses.json"

    try:
        with open(gold_qas_file, 'r', encoding='utf-8') as f:
            gold_data = json.load(f)
    except Exception as e:
        print(f"Error loading gold QAs: {e}")
        return

    try:
        with open(o7_responses_file, 'r', encoding='utf-8') as f:
            o7_data = json.load(f)
    except Exception as e:
        print(f"Error loading O7 responses: {e}")
        return

    # 3. Setup output folder and checkpoint manager.
    output_dir = "validator_outputs"
    os.makedirs(output_dir, exist_ok=True)
    checkpoint_file = "validator_checkpoint.json"
    checkpoint_manager = CheckpointManager(checkpoint_file)
    processed_categories = checkpoint_manager.load()

    # 4. Iterate through categories (gold_data keys).
    total_categories = len(gold_data)
    # for category in gold_data:
    for idx, category in enumerate(gold_data.keys(), start=1):
        if category in processed_categories:
            print(f"Skipping already processed category: {category}")
            continue

        if category not in o7_data:
            print(f"Category '{category}' not found in O7 responses. Skipping.")
            continue

        gold_items = gold_data[category]
        o7_items = o7_data[category]

        print(f"\nProcessing category ({idx}/{total_categories}): {category}")
        if len(gold_items) != len(o7_items):
            print(f"Warning: Mismatched lengths for category {category} (gold={len(gold_items)}, o7={len(o7_items)})")

        validator_results = []
        # 5. Loop over each question.
        for i, gold_qa in enumerate(gold_items):
            question = gold_qa.get("question", "")
            proof = gold_qa.get("proof", "")
            correct_answer = gold_qa.get("answer", "")

            print(f"—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—\n"
                  f"Processing question {i+1}:\n{question}\n")

            o7_answer_entry = o7_items[i] if i < len(o7_items) else {}
            if not o7_answer_entry:
                continue

            o7_answer = extract_o7_answer(o7_answer_entry)

            # 6. Call the validator agent with placeholders.
            validation_output = validator_agent.run(
                question=question,
                correct_answer=correct_answer,
                proof=proof,
                given_answer=o7_answer
            )

            # Parse the validation output into separate fields.
            assessment, score = parse_validation(validation_output)

            validator_results.append({
                "question": question,
                "correct_answer": correct_answer,
                "proof": proof,
                "given_answer": o7_answer,
                "assessment": assessment,
                "score": score
            })

        print(f"—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—")
        # 7. Write out a JSON file with the validation results for this category.
        output_file = os.path.join(output_dir, f"{sanitize_filename(category)}.json")
        try:
            with open(output_file, 'w', encoding='utf-8') as out_f:
                json.dump(validator_results, out_f, indent=4)
            print(f"Validator results saved to {output_file}")
        except Exception as e:
            print(f"Error writing validator results for category '{category}': {e}")
            continue

        # Mark this category as processed.
        processed_categories.add(category)
        checkpoint_manager.save(processed_categories)
        print(f"Finished processing category: {category}")


if __name__ == '__main__':
    main()
