import asyncio

# Fix for Python 3.13 Windows socket issue
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AMR Prediction API running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    
    content = await file.read()
    
    # fake prediction example
    result = {
        "Ciprofloxacin": "Resistant",
        "Ampicillin": "Susceptible",
        "Tetracycline": "Resistant"
    }

    return {
        "filename": file.filename,
        "prediction": result
    }