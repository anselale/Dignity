#!/usr/bin/env python3
import os
import json


def sanitize_category_name(filename):
    """Convert a filename (without extension) into a human-friendly category title."""
    base = os.path.splitext(filename)[0]
    return base.replace('_', ' ')


def convert_json_to_markdown(json_data, category_title):
    """
    Convert a list of validation objects into Markdown.
    Each object is expected to have keys:
      - "question"
      - "correct_answer"
      - "proof"
      - "given_answer"
      - "assessment"
      - "score"
    The output is formatted for easy reading.
    """
    markdown_lines = [f"# {category_title}\n"]
    for idx, qa in enumerate(json_data, start=1):
        question = qa.get("question", "")
        correct_answer = qa.get("correct_answer", "")
        proof = qa.get("proof", "")
        given_answer = qa.get("given_answer", "")
        assessment = qa.get("assessment", "")
        score = qa.get("score", "")

        markdown_lines.append(f"## Question {idx} - Score: " + str(score))
        markdown_lines.append("### Question")
        markdown_lines.append("")
        markdown_lines.append(question)
        markdown_lines.append("")
        markdown_lines.append("### Correct Answer")
        markdown_lines.append("")
        markdown_lines.append(correct_answer)
        markdown_lines.append("")
        markdown_lines.append("### Assessment")
        markdown_lines.append("")
        markdown_lines.append(assessment)
        markdown_lines.append("### Given Answer")
        markdown_lines.append("")
        markdown_lines.append("~~~")
        markdown_lines.append(given_answer)
        markdown_lines.append("~~~")
        markdown_lines.append("")
        markdown_lines.append("### Proof")
        markdown_lines.append("")
        markdown_lines.append("~~~")
        markdown_lines.append(proof)
        markdown_lines.append("~~~")
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")

    return "\n".join(markdown_lines)


def main():
    # Folder where the validator JSON files are stored.
    responses_folder = "validator_outputs"
    # Output folder for Markdown files.
    output_folder = "validator_markdown"
    os.makedirs(output_folder, exist_ok=True)

    if not os.path.exists(responses_folder):
        print(f"Responses folder '{responses_folder}' does not exist.")
        return

    for filename in os.listdir(responses_folder):
        if filename.lower().endswith('.json'):
            file_path = os.path.join(responses_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Create a human-friendly title based on the filename.
            category_title = sanitize_category_name(filename)
            # Convert the JSON data to Markdown.
            markdown_content = convert_json_to_markdown(json_data, category_title)
            # Write the Markdown to a file with the same basename.
            md_filename = os.path.splitext(filename)[0] + ".md"
            md_file_path = os.path.join(output_folder, md_filename)
            try:
                with open(md_file_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(markdown_content)
                print(f"Converted {filename} to Markdown: {md_file_path}")
            except Exception as e:
                print(f"Error writing to {md_file_path}: {e}")


if __name__ == '__main__':
    main()
