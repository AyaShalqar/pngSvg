import io

from PIL import Image
from rembg import remove


# Load your input image
def gemini_background_removal(image: bytes) -> Image.Image:
    bio = io.BytesIO(image)
    image = Image.open(bio)
    output_data = remove(image)

    return output_data