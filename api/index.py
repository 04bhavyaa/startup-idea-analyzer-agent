import sys
sys.path.append('..')

from src.workflow import analyze_idea  # Adjust import as needed
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/")
async def analyze(request: Request):
    data = await request.json()
    idea = data.get("idea")
    if not idea:
        return JSONResponse({"error": "Missing 'idea' in request."}, status_code=400)
    result = analyze_idea(idea)
    return JSONResponse({"result": result})
