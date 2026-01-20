from fastapi import APIRouter, UploadFile, File
from starlette.concurrency import run_in_threadpool

from src.services.delete_background import gemini_background_removal
from src.services.gemini_service import gemini_background_white
from src.services.svg_converter import vectorize_image

router = APIRouter()


@router.post("/run-scripts/")
async def run_scripts(file: UploadFile = File(...)):
    image_bytes = await file.read()
    output_image = gemini_background_white(image_bytes)
    no_bg_image = gemini_background_removal(output_image)
    svg_url = await run_in_threadpool(vectorize_image, no_bg_image)

    return {
        "status": "success",
        "svg_url": svg_url,
    }
