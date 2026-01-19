from fastapi import FastAPI
from app.routes.script_routes import router


app = FastAPI()
app.include_router(router, prefix="/api")

# @app.post("/run-scripts/")
# def main():
#       print("=== Запуск gemini ===")
#       gemini_background_white()

#       print("\n=== Запуск deleteBackground ===")
#       gemini_background_removal()

#       print("\n=== Готово! ===")


# if __name__ == "__main__":
#     main()