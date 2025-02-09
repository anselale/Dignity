#!/usr/bin/env python3
import os
import json

def aggregate_validator_outputs():
    responses_folder = 'validator_outputs'
    output_file = 'validator_outputs.json'
    aggregated_data = {}

    if not os.path.exists(responses_folder):
        print(f"Folder '{responses_folder}' does not exist.")
        return

    # Iterate through all JSON files in the validator_outputs folder.
    for filename in os.listdir(responses_folder):
        if filename.lower().endswith('.json'):
            # Use the file name (without extension) as the category key.
            category = os.path.splitext(filename)[0]
            file_path = os.path.join(responses_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                aggregated_data[category] = data
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    # Write the aggregated data to a single JSON file.
    try:
        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(aggregated_data, out_f, indent=4, sort_keys=True)
        print(f"Aggregated validator outputs saved to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == '__main__':
    aggregate_validator_outputs()
