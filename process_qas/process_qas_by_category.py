# process_qas_by_category.py
import os
import json
import time
from o7 import O7
from checkpoint_manager import CheckpointManager

def sanitize_category(category):
    return category.replace(' ', '_').replace('/', '_')

class ProcessQAsByCategory:
    def __init__(self, qas_file, output_dir='o7responses', max_retries=3, retry_delay=5):
        self.qas_file = qas_file
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.output_dir = output_dir
        self.o7 = O7()

        # Instantiate a checkpoint manager for processing.
        self.checkpoint_manager = CheckpointManager("processed_categories.json")
        self.processed_categories = self.checkpoint_manager.load()

    def process(self):
        # Load aggregated QAs.
        try:
            print("Loading QAS JSON file...")
            with open(self.qas_file, "r", encoding="utf-8") as f:
                qa_data = json.load(f)
        except Exception as e:
            print(f"Error loading {self.qas_file}: {e}")
            return

        total_categories = len(qa_data)
        # Enumerate sorted keys with an index starting from 1.
        for idx, category in enumerate(sorted(qa_data.keys()), start=1):
            if category in self.processed_categories:
                print(f"Skipping already processed category: {category}")
                continue

            safe_category = sanitize_category(category)
            file_path = os.path.join(self.output_dir, f"{safe_category}.json")
            if os.path.exists(file_path):
                os.remove(file_path)

            # print(f"\nProcessing category: {category}")
            print(f"\nProcessing category ({idx}/{total_categories}): {category}")
            qa_list = qa_data[category]
            all_success = True

            for idx_q, qa in enumerate(qa_list, start=1):
                question = qa.get("question", "").strip()
                print(f"—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—\n"
                      f"Processing question {idx_q}:\n{question}\n")
                success = self.process_question(category, question)
                if not success:
                    print(f"Failed to process question {idx_q} after {self.max_retries} attempts.")
                    all_success = False
                    break

            print(f"—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—")
            if all_success:
                self.processed_categories.add(category)
                self.checkpoint_manager.save(self.processed_categories)
                print(f"Finished processing category: {category}")
            else:
                print(f"Category '{category}' encountered errors; it will be retried later.")

    def process_question(self, category, question):
        attempts = 0
        while attempts < self.max_retries:
            try:
                response = self.o7.run_o7(question)
                self.write_response(category, response)
                return True
            except Exception as e:
                attempts += 1
                print(f"Error processing question (attempt {attempts}/{self.max_retries}): {e}")
                time.sleep(self.retry_delay)
        return False

    def write_response(self, category, json_object):
        os.makedirs(self.output_dir, exist_ok=True)
        safe_category = sanitize_category(category)
        file_path = os.path.join(self.output_dir, f"{safe_category}.json")
        try:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, 'r+', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
                    data.append(json_object)
                    f.seek(0)
                    json.dump(data, f, indent=2, sort_keys=True)
                    f.truncate()
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([json_object], f, indent=2, sort_keys=True)
            print(f"Response appended to {file_path}")
        except Exception as e:
            print(f"Error writing response to file {file_path}: {e}")

if __name__ == '__main__':
    qas_input_file = "../qa_gen/qas.json"
    print('Initializing processing of QAs...')
    processor = ProcessQAsByCategory(qas_input_file)
    processor.process()