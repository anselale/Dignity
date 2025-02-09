# qa_generation.py
import os
from agentforge.agent import Agent
from checkpoint_manager import CheckpointManager

def load_categories(filename='../categories.txt'):
    with open(filename, 'r') as file:
        cats = [line.strip() for line in file if line.strip()]
    return cats

def sanitize_category(category):
    return category.replace(' ', '_').replace('/', '_')

def main():
    # Instantiate the checkpoint manager with a dedicated checkpoint file.
    checkpoint_manager = CheckpointManager("qa_gen_checkpoint.json")
    processed_categories = checkpoint_manager.load()

    # Instantiate our QA generation agent.
    qa_gen_agent = Agent('QAGenAgent')

    categories = load_categories()
    output_dir = 'qas'
    os.makedirs(output_dir, exist_ok=True)

    for category in categories:
        if category in processed_categories:
            print(f"Skipping {category} (already processed).")
            continue

        try:
            print(f"Generating QA pairs for category: {category}")
            results = qa_gen_agent.run(question_amount=4, topic=category)

            # sanitized_category = sanitize_category(category = os.path.splitext(category)[0])
            sanitized_category = sanitize_category(category = category)
            output_file = os.path.join(output_dir, f"{sanitized_category}.md")
            with open(output_file, 'w') as f:
                f.write(results)
            print(f"Saved QA pairs for '{category}' in file: {output_file}\n")

            # Mark the category as processed.
            processed_categories.add(category)
            checkpoint_manager.save(processed_categories)

        except Exception as e:
            print(f"Error generating QA pairs for '{category}': {e}")

if __name__ == '__main__':
    main()