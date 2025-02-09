# convert_o7responses_to_md.[y
import os
import json


def sanitize_category_name(filename):
    """Convert a filename (without extension) into a human-friendly category title."""
    base = os.path.splitext(filename)[0]
    # Replace underscores with spaces and preserve original case.
    return base.replace('_', ' ')

def sanitize_category(category):
    return "".join(c if c.isalnum() else "_" for c in category)

def convert_json_to_markdown(json_data, category_title):
    """
    Convert a list of response objects (from o7) to markdown.
    Each response object is expected to be a list of dictionaries,
    where the dictionary with key "user" contains the question, and
    the dictionary with key "assistant" contains the answer.
    """
    markdown_lines = [f"# {category_title}\n"]
    for idx, response_obj in enumerate(json_data, start=1):
        # Try to extract the question (from key "user") and answer (from key "assistant")
        question_text = ""
        answer_text = ""
        for entry in response_obj:
            if "user" in entry:
                question_text = entry["user"]
            elif "assistant" in entry:
                answer_text = entry["assistant"]

        markdown_lines.append(f"## Question {idx}")
        markdown_lines.append("")
        markdown_lines.append(question_text)
        markdown_lines.append("")
        markdown_lines.append("### Answer")
        markdown_lines.append("")
        markdown_lines.append("~~~")
        markdown_lines.append(answer_text)
        markdown_lines.append("~~~")
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")

    return "\n".join(markdown_lines)


def main():
    # Folder where the o7 responses are stored as JSON.
    responses_folder = "o7responses"
    # Output folder for markdown files.
    output_folder = "markdown_responses"
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

            # Create a human-friendly category title based on the file name.
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
