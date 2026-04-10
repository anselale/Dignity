import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentforge.apis.lm_studio_api import LMStudioVision
from pathlib import Path

def test_lm_studio_vision():
    model = LMStudioVision(model_name="gemma-4")

    # Put a test image in your Tests folder
    image_path = Path(__file__).parent / "img.png"

    if not image_path.exists():
        print(f"No test image found at {image_path}")
        print("Add a test_image.png to your Tests folder and retry.")
        return

    prompt = {
        "system": "You are a helpful assistant that describes images.",
        "user": "What do you see in this image?"
    }

    try:
        response = model.generate(
            model_prompt=prompt,
            images=[str(image_path)],
            agent_name="VisionTest",
            host_url="http://localhost:1234/v1/chat/completions"
        )
        print(f"\n--- Response ---\n{response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_lm_studio_vision()