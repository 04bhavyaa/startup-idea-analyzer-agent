from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sys
sys.path.append('..')
from src.workflow import analyze_idea

app = FastAPI()

@app.post("/")
async def analyze(request: Request):
    data = await request.json()
    idea = data.get("idea")
    if not idea:
        return JSONResponse({"error": "Missing 'idea' in request."}, status_code=400)
    result = await analyze_idea(idea)
    return JSONResponse({"result": result})
