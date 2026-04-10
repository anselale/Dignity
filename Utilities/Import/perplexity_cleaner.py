import os
import re

# --- DYNAMIC PATH FIX ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRTY_DIR = os.path.join(SCRIPT_DIR, "Dirty")
CLEAN_DIR = os.path.join(SCRIPT_DIR, "Clean")

os.makedirs(DIRTY_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)


# ------------------------

def clean_perplexity_file(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Split the document by Perplexity's turn separator '---'
    turns = re.split(r'\n-{3,}\n', content)
    cleaned_turns = []

    for turn in turns:
        turn = turn.strip()
        if not turn:
            continue

        # 2. Split into lines to cleanly pop references and artifacts from the bottom up
        lines = turn.split('\n')
        while lines:
            last_line = lines[-1].strip()

            # Pop completely empty lines at the bottom
            if not last_line:
                lines.pop()
                continue

            # Identify references, asterisms, and Perplexity's hidden metadata spans
            is_ref_or_artifact = (
                    bool(re.match(r'^\[\^?[\w\s,_]+\]:?', last_line)) or  # Catches [1]: or [^1_1]:
                    bool(re.match(r'^\d+\.', last_line)) or  # Catches 1.
                    last_line.lower().strip('# \t:') in ['sources', 'references', 'citations'] or
                    last_line.startswith('http') or
                    '⁂' in last_line or  # Catches the asterism
                    '<span style="display:none">' in last_line  # Catches hidden citation spans
            )

            if is_ref_or_artifact:
                lines.pop()
            else:
                break  # We've hit the actual conversation text!

        turn_text = '\n'.join(lines)

        # 3. Strip inline citation anchors AND their attached links (e.g., [^1_1])
        turn_text = re.sub(r'\[\^?[\w\s,_]+\](?:\([^\)]+\))?', '', turn_text)

        # 4. Strip standard markdown links, keeping ONLY the text [Text](URL) -> Text
        turn_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', turn_text)

        # 5. Destroy any remaining raw URLs
        turn_text = re.sub(r'https?://[^\s<>"\'\]\)]+', '', turn_text)

        # 6. Remove <> HTML tags (This nukes the <img> tag from the file upload!)
        turn_text = re.sub(r'<[^>]+>', '', turn_text)

        # 7. Strip the H1/H2 markdown from the first user line
        turn_text = re.sub(r'^#+\s+', '', turn_text.lstrip())

        # Clean up any massive newline gaps left behind by the deletions
        turn_text = re.sub(r'\n{3,}', '\n\n', turn_text).strip()

        if turn_text:
            # 8. Wrap the entire cohesive turn in explicit interaction blocks
            cleaned_turns.append(f"[INTERACTION_BLOCK]\n{turn_text}\n[/INTERACTION_BLOCK]")

    # Reassemble the file
    final_content = '\n\n'.join(cleaned_turns)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"[+] Cleaned: {os.path.basename(file_path)}")


def main():
    print("=== Perplexity Log Cleaner ===")

    dirty_files = [f for f in os.listdir(DIRTY_DIR) if f.endswith('.md') or f.endswith('.txt')]

    if not dirty_files:
        print(f"[!] No files found in {DIRTY_DIR}. Drop your exports there and run again.")
        return

    processed_count = 0
    for filename in dirty_files:
        file_path = os.path.join(DIRTY_DIR, filename)
        output_path = os.path.join(CLEAN_DIR, filename)

        clean_perplexity_file(file_path, output_path)
        processed_count += 1

    print(f"\n[✓] Successfully cleaned {processed_count} files. Ready for the LogParserAgent!")


if __name__ == "__main__":
    main()