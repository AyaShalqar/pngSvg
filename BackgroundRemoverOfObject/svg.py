from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
FAL_KEY = os.getenv("FAL_KEY")

client = OpenAI(
    base_url="https://external.api.recraft.ai/v1",
    api_key=FAL_KEY
)
def vectorize_image(image_path: str) -> str:
    """
    Векторизует изображение и возвращает ссылку на SVG.
    """
    with open(image_path, "rb") as f:
        response = client.post(
            path="/images/vectorize",
            cast_to=object,
            options={"headers": {"Content-Type": "multipart/form-data"}},
            files={"file": f},
        )

    return response["image"]["url"]
# source venv/bin/activate



# import replicate
# import requests
# import uuid
# import os
# from pathlib import Path
# import httpx
# import fal_client
# from dotenv import load_dotenv
# from openai import OpenAI


# client = OpenAI(base_url='https://external.api.recraft.ai/v1', api_key=_RECRAFT_API_TOKEN)

# response = client.post(
#     path='/images/vectorize',
#     cast_to=object,
#     options={'headers': {'Content-Type': 'multipart/form-data'}},
#     files={'file': open('image.png', 'rb')},
# )
# print(response['image']['url'])

# load_dotenv()
# ALLOWED_EXTENSIONS = {"image/png", "image/jpeg", "image/webp"}

# def svg_to_png(image_path: str) -> str:

#     if not image_path.lower().endswith(ALLOWED_EXTENSIONS):
#         raise ValueError("Invalid file type. Please upload PNG/JPG/WEBP.")
#     if not os.getenv("FAL_API_KEY"):
#         raise ValueError("FAL_API_KEY not set in environment variables.")
    
#     print("➡ Отправка изображения в Recraft Vectorize API...")

#     with open(image_path, "rb") as file:
#         output = replicate.run(
#             "recraft-ai/recraft-vectorize",
#             input={
#                 "image": file
#             }
#         )






# POST https://external.api.recraft.ai/v1/images/vectorize