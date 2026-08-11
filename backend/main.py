from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

app = FastAPI(title="OpenVideoStudio API", version="1.0.0")

# Enable CORS (useful if developing frontend on a different port later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure backend directory is in sys.path so 'engines' can be imported regardless of execution path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

from pydantic import BaseModel
import asyncio
from fastapi.responses import FileResponse, Response

# --- Models ---
class PlanRequest(BaseModel):
    prompt: str
    duration: int = 15
    provider: str = "gemini"

class VideoRequest(BaseModel):
    plan: dict
    # Additional options can be added here

# --- API Endpoints ---

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204) # No content, prevents 404 logs

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

import time
from fastapi.staticfiles import StaticFiles

# Create output directory for final videos
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

@app.post("/api/generate_video")
async def api_generate_video(request: VideoRequest):
    try:
        plan = request.plan
        language = plan.get("language", "te")
        scenes = plan.get("scenes", [])
        
        if not scenes:
            raise ValueError("No scenes found in the plan.")

        import uuid
        job_id = str(uuid.uuid4())[:8]
        temp_dir = os.path.join(BASE_DIR, "temp", job_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 1. Combine narration & generate audio
        from engines.tts_engine import generate_audio
        full_text = " ".join([scene.get("narration_text", "") for scene in scenes])
        audio_path = os.path.join(temp_dir, "audio.mp3")
        print("Generating audio...")
        generate_audio(full_text, audio_path, language)
        
        # 2. Generate subtitles
        from engines.subtitle_engine import generate_srt
        srt_path = os.path.join(temp_dir, "subtitles.srt")
        print("Generating subtitles...")
        generate_srt(audio_path, srt_path, model_size="base")
        
        # 3. Download stock videos
        from engines.asset_engine import search_stock_video, download_video
        video_paths = []
        print("Downloading stock videos...")
        for i, scene in enumerate(scenes):
            query = scene.get("search_query", "technology")
            video_url = search_stock_video(query, orientation="portrait")
            scene_path = os.path.join(temp_dir, f"scene_{i}.mp4")
            download_video(video_url, scene_path)
            video_paths.append(scene_path)
            
        # 4. Compose final video
        from engines.video_engine import compose_video
        final_filename = f"final_video_{job_id}.mp4"
        final_path = os.path.join(OUTPUT_DIR, final_filename)
        print("Composing video...")
        compose_video(video_paths, audio_path, final_path, srt_path)
        
        return {
            "status": "success", 
            "message": "Video rendered successfully!",
            "video_url": f"/output/{final_filename}"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
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
