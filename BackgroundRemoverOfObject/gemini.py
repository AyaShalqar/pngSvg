from google import genai
from google.genai.errors import ClientError
from dotenv import load_dotenv
import os
import time
from PIL import Image

load_dotenv()

def gemini_background_white(imager_path: str, max_retries: int = 3) -> str:
    api_key1 = os.getenv("GEMINI_TOKEN")
    client = genai.Client(api_key=api_key1)

    prompt = """
Use the uploaded image as the source.

Precisely cut out the main object from the photo, completely removing the background.

Preserve the original shape, proportions, and details of the object — do not modify, stylize, or add anything.

Place the object centered on a pure white background (#FFFFFF).

Edges must be clean, sharp, and natural, with no halos, artifacts, or blur.

Neutral lighting, no shadows.

The final result should look like a high-quality professional asset for UI, e-commerce, or product catalogs.

No text, no watermarks, no extra objects.
"""

    image = Image.open(imager_path)

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt, image],
            )
            break
        except ClientError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 60 * (attempt + 1)
                print(f"Rate limit hit. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise
    output_path = "uploads/generated_image.png"

    for part in response.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)

    return output_path



