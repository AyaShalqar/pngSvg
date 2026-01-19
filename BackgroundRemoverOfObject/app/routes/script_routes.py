import shutil
from fastapi import APIRouter, UploadFile, File
from gemini import gemini_background_white
from deleteBackground import gemini_background_removal
from svg import vectorize_image
import requests

router = APIRouter()

@router.post("/run-scripts/")
async def run_scripts(file: UploadFile = File(...)):
    # if not file.content_type or not file.content_type.startswith("image/"):
    #     return {"error": "Invalid file type. Please upload an image."}
    
    input_path = f"uploads/{file.filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_path_gemini = gemini_background_white(input_path)
    output_path_delete = gemini_background_removal(output_path_gemini)

    svg_url = vectorize_image(output_path_delete)

    svg_path = f"uploads/{file.filename}.svg"
    download_image(svg_url, svg_path)
    print (svg_url)



    return {
        "status": "success",
        "svg_url": svg_url,
        "svg_file": svg_path
    }


def download_image(url: str, save_path: str) -> None:
    response = requests.get(url)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)