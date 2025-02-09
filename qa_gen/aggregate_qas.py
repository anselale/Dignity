import os
import re
import json

def clean_value(text):
    """
    Remove any leading or trailing lines that contain only dashes (---),
    with or without extra whitespace.
    """
    lines = text.splitlines()
    # Remove leading lines that are just dashes
    while lines and lines[0].strip() == '---':
        lines.pop(0)
    # Remove trailing lines that are just dashes
    while lines and lines[-1].strip() == '---':
        lines.pop()
    # Return the cleaned text
    return "\n".join(lines).strip()

def sanitize_category(name):
    return name.replace(' ', '_').replace('/', '_')

def extract_qa_pairs(md_text):
    """
    Extracts QA pairs from the markdown text.
    Expects each QA pair to follow this pattern:

    **Question <num>:**
    <question text>

    **Answer <num>:**
    <answer text>

    **Proof <num>:**
    <proof text>

    Returns a list of dictionaries with keys "question", "answer", and "proof".
    """
    pattern = re.compile(
        r"\*\*Question\s+\d+:\*\*\s*(.*?)\s*"
        r"\*\*Answer\s+\d+:\*\*\s*(.*?)\s*"
        r"\*\*Proof\s+\d+:\*\*\s*(.*?)(?=\*\*Question\s+\d+:|$)",
        re.DOTALL
    )
    pairs = []
    for match in pattern.finditer(md_text):
        # Extract and clean each value.
        question = clean_value(match.group(1).strip())
        answer   = clean_value(match.group(2).strip())
        proof    = clean_value(match.group(3).strip())
        new_pair = {
            "question": question,
            "answer": answer,
            "proof": proof
        }
        pairs.append(new_pair)
    return pairs

def main():
    qas_folder = 'qas'
    output_file = 'qas.json'
    qa_data = {}

    if not os.path.exists(qas_folder):
        print(f"Folder '{qas_folder}' does not exist.")
        return

    # Iterate through all markdown files in the qas folder.
    for file_name in os.listdir(qas_folder):
        if file_name.lower().endswith('.md'):
            category = sanitize_category(os.path.splitext(file_name)[0])
            file_path = os.path.join(qas_folder, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            pairs = extract_qa_pairs(content)
            if pairs:
                qa_data[category] = pairs
            else:
                print(f"No QA pairs found in {file_name}")

    # Write out the aggregated QA pairs to a JSON file.
    with open(output_file, 'w', encoding='utf-8') as out_f:
        json.dump(qa_data, out_f, indent=2, sort_keys=True)

    print(f"QA data aggregated into {output_file}")

if __name__ == '__main__':
    main()
