import io
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://external.api.recraft.ai/v1",
    api_key=os.getenv("FAL_KEY"),
    timeout=180,
    max_retries=2
)

from PIL import Image


def vectorize_image(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    response = client.post(
        path="/images/vectorize",
        cast_to=object,
        options={"headers": {"Content-Type": "multipart/form-data"}},
        files={"file": buf},
    )
    return response["image"]["url"]
