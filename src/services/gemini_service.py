import os
import time
from io import BytesIO

from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv()

PROMPT = """
Use the uploaded image as the source.

Precisely cut out the main object from the photo, completely removing the background.

Preserve the original shape, proportions, and details of the object — do not modify, stylize, or add anything.

Place the object centered on a pure white background (#FFFFFF).

Edges must be clean, sharp, and natural, with no halos, artifacts, or blur.

Neutral lighting, no shadows.

The final result should look like a high-quality professional asset for UI, e-commerce, or product catalogs.

No text, no watermarks, no extra objects.
""".strip()


def gemini_background_white(image_bytes: bytes, max_retries: int = 3) -> bytes:
    api_key = os.getenv("GEMINI_TOKEN")
    if not api_key:
        raise RuntimeError("GEMINI_TOKEN is not set")

    client = genai.Client(api_key=api_key)
    src_img = Image.open(BytesIO(image_bytes))

    response = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[PROMPT, src_img],
            )
            break
        except ClientError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 60 * (attempt + 1)
                time.sleep(wait_time)
            else:
                raise

    out_img_bytes = None
    for part in getattr(response, "parts", []) or []:
        if getattr(part, "inline_data", None) is not None:
            out_img_bytes = part.as_image().image_bytes
            break
        if getattr(part, "text", None):
            print(part.text)

    if out_img_bytes is None:
        raise RuntimeError("No image returned by the model")

    out_pil = Image.open(BytesIO(out_img_bytes)).convert("RGB")
    out_buf = BytesIO()
    out_pil.save(out_buf, format="PNG", optimize=True)
    return out_buf.getvalue()
