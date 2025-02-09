# create_finetuning_dataset.py
import os
import json

# Configuration: set your system prompt and score threshold here.
SYSTEM_PROMPT = "You are a thinking agent responsible for developing a detailed, step-by-step thought process in response to a request, problem, or conversation. Your task is to break down the situation or question into a structured reasoning process. If feedback is provided, integrate it into your thought process for refinement."
SCORE_THRESHOLD = 70

def sanitize_category(filename):
    """
    Converts a filename (without extension) into a human-friendly category.
    For example, "Astro-ph_CO.json" becomes "Astro-ph CO".
    """
    base = os.path.splitext(filename)[0]
    return base.replace('_', ' ')

def main():
    # Folder containing the per-category validator JSON files.
    input_folder = "validator_outputs"
    # Output JSONL file for fine-tuning.
    output_file = "finetuning_dataset.jsonl"

    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' not found.")
        return

    accepted_count = 0
    rejected_count = 0
    total_with_scores = 0
    min_score = None
    max_score = None

    # We'll store details about rejected examples.
    rejected_examples = []

    with open(output_file, 'w', encoding='utf-8') as out_f:
        # Iterate over each JSON file in the validator_outputs folder.
        for filename in os.listdir(input_folder):
            if not filename.lower().endswith('.json'):
                continue

            category = sanitize_category(filename)
            file_path = os.path.join(input_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    examples = json.load(f)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Use enumerate to get a question number for each example.
            for idx, example in enumerate(examples, start=1):
                score = example.get("score", None)
                if score is None:
                    continue
                try:
                    score_int = int(score)
                except Exception as e:
                    print(f"Could not convert score '{score}' to int: {e}")
                    continue

                total_with_scores += 1
                if min_score is None or score_int < min_score:
                    min_score = score_int
                if max_score is None or score_int > max_score:
                    max_score = score_int

                question = example.get("question", "").strip()

                # Only include examples that meet or exceed the threshold.
                if score_int < SCORE_THRESHOLD:
                    rejected_count += 1
                    rejected_examples.append({
                        "category": category,
                        "question_number": idx,
                        "question": question,
                        "score": score_int
                    })
                    continue

                given_answer = example.get("given_answer", "").strip()

                # Build the finetuning example.
                finetune_example = {
                    "system": SYSTEM_PROMPT,
                    "user": question,
                    "assistant": given_answer
                }
                # Write the example as a single line JSON object.
                out_f.write(json.dumps(finetune_example) + "\n")
                accepted_count += 1

    print(f"\nCreated finetuning dataset with {accepted_count} examples in '{output_file}'")
    print(f"Score threshold: {SCORE_THRESHOLD}")
    print(f"Rejected examples (score below threshold): {rejected_count}")
    if total_with_scores > 0:
        print(f"Minimum score encountered: {min_score}")
        print(f"Maximum score encountered: {max_score}")
    else:
        print("No examples with valid scores were found.")

    if rejected_examples:
        print("\nDetails of rejected examples:")
        for rej in rejected_examples:
            print(f"Category: {rej['category']}, Question #{rej['question_number']}, Score: {rej['score']}")

if __name__ == '__main__':
    main()