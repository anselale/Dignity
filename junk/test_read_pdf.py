import sys
from pathlib import Path

sys.path.insert(0, '..')  # adjust if needed to reach your project root

from agentforge.tools.get_text import GetText


def test_pdf():
    gettext = GetText()
    filename = str(Path(__file__).parent / "test_pdf.pdf")

    try:
        text = gettext.read_file(filename)
        print(f"\n--- Extracted Text (first 1000 chars) ---\n")
        print(text[:1000])
        print(f"\n--- Total characters extracted: {len(text)} ---")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_pdf()