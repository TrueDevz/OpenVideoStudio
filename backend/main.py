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
from fastapi import BackgroundTasks
import uuid
import json

# Create output directory for final videos
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

# Simple in-memory job store for demo purposes
jobs = {}

async def process_video_job(job_id: str, plan: dict):
    jobs[job_id] = {"status": "processing", "message": "Starting rendering..."}
    try:
        language = plan.get("language", "te")
        scenes = plan.get("scenes", [])
        
        if not scenes:
            raise ValueError("No scenes found in the plan.")

        temp_dir = os.path.join(BASE_DIR, "temp", job_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 1. Combine narration & generate audio
        jobs[job_id]["message"] = "Generating AI Voiceover..."
        from engines.tts_engine import generate_audio_async
        full_text = " ".join([scene.get("narration_text", "") for scene in scenes])
        audio_path = os.path.join(temp_dir, "audio.mp3")
        await generate_audio_async(full_text, audio_path, language)
        
        # 2. Generate subtitles
        jobs[job_id]["message"] = "Transcribing subtitles with Whisper..."
        from engines.subtitle_engine import generate_srt
        srt_path = os.path.join(temp_dir, "subtitles.srt")
        generate_srt(audio_path, srt_path, model_size="base")
        
        # 3. Download stock videos
        jobs[job_id]["message"] = "Fetching free stock footage..."
        from engines.asset_engine import search_stock_video, download_video
        video_paths = []
        for i, scene in enumerate(scenes):
            query = scene.get("search_query", "technology")
            video_url = search_stock_video(query, orientation="portrait")
            scene_path = os.path.join(temp_dir, f"scene_{i}.mp4")
            download_video(video_url, scene_path)
            video_paths.append(scene_path)
            
        # 4. Compose final video
        jobs[job_id]["message"] = "Rendering final video (FFmpeg)..."
        from engines.video_engine import compose_video
        final_filename = f"final_video_{job_id}.mp4"
        final_path = os.path.join(OUTPUT_DIR, final_filename)
        compose_video(video_paths, audio_path, final_path, srt_path)
        
        jobs[job_id]["status"] = "success"
        jobs[job_id]["video_url"] = f"/output/{final_filename}"
        jobs[job_id]["message"] = "Video rendered successfully!"
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        jobs[job_id]["status"] = "error"
        jobs[job_id]["message"] = str(e)


@app.post("/api/generate_video")
async def api_generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(process_video_job, job_id, request.plan)
    return {"status": "accepted", "job_id": job_id, "message": "Video rendering started in background."}

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    if job_id in jobs:
        return jobs[job_id]
    return {"status": "error", "message": "Job not found"}

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
