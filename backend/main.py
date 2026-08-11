from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="OpenVideoStudio API", version="1.0.0")

# Enable CORS (useful if developing frontend on a different port later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

from pydantic import BaseModel
import asyncio

# --- Models ---
class PlanRequest(BaseModel):
    prompt: str
    duration: int = 15
    provider: str = "gemini"

class VideoRequest(BaseModel):
    plan: dict
    # Additional options can be added here

# --- API Endpoints ---

@app.get("/api/status")
async def get_status():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "OpenVideoStudio API is running!"}

@app.post("/api/generate_plan")
async def api_generate_plan(request: PlanRequest):
    try:
        from engines.llm_engine import generate_video_plan
        plan = generate_video_plan(request.prompt, request.duration, request.provider)
        return {"status": "success", "plan": plan}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/generate_video")
async def api_generate_video(request: VideoRequest):
    # This is a simplified mock of the full pipeline for the UI to connect to.
    # A real implementation would trigger a background task and use websockets for progress.
    try:
        plan = request.plan
        # In a real scenario, we would:
        # 1. Loop through scenes, generate audio (tts_engine)
        # 2. Get subtitles (subtitle_engine)
        # 3. Download stock videos (asset_engine)
        # 4. Compose final video (video_engine)
        
        # Simulating processing time
        await asyncio.sleep(5)
        
        return {
            "status": "success", 
            "message": "Video rendered successfully!",
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4" # Placeholder for demo
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Static File Serving (Frontend) ---
# Mount the frontend directory to serve all static files (index.html, css, js)
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"WARNING: Frontend directory not found at {FRONTEND_DIR}")

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
