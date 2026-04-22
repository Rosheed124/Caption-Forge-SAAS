from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import shutil
import subprocess
from engine import generate_and_burn_subtitles

app = FastAPI(title="CaptionForge Subtitle API", version="1.0.0")

# Setup CORS for the frontend HTML to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories for processing
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_video_duration(filepath: str) -> float:
    try:
        command = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of",
            "default=noprint_wrappers=1:nokey=1", filepath
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return float(result.stdout.strip())
    except Exception:
        return 0.0

# Basic in-memory status dictionary (In production use Redis or Postgres)
# Status: "processing", "completed", "error"
PROCESSING_JOBS = {}


# --- Background Worker ---
def process_video_job(job_id: str, input_path: str, output_path: str, user_tier: str, font: str = "Arial", highlight_font: str = None):
    """
    Background worker that calls the engine.py logic.
    Applies the Launch/Pricing tiers. Includes premium highlight font for combinations.
    """
    PROCESSING_JOBS[job_id] = {"status": "processing", "progress": "Listening and generating text..."}
    try:
        # Generate the subtitles mixed with highlight font
        srt_filename = generate_and_burn_subtitles(input_path, output_path, font, highlight_font)
        
        # Mark Complete
        PROCESSING_JOBS[job_id] = {
            "status": "completed", 
            "download_url": f"/download/{job_id}",
            "download_srt_url": f"/download_srt/{job_id}",
            "srt_file": srt_filename,
            "marketing_event": "Feature used: Automatic Subtitles" # For Launch Analytics
        }
    except Exception as e:
        PROCESSING_JOBS[job_id] = {"status": "error", "error_message": str(e)}
        print(f"Error processing job {job_id}: {str(e)}")
    finally:
        # Cleanup original upload to save server disk space
        if os.path.exists(input_path):
            os.remove(input_path)


# --- Endpoints ---

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...), tier: str = Form("free"), font: str = Form("Arial"), highlight_font: str = Form(None)):
    """
    Upload a video to the SaaS platform.
    Pricing Tier Logic (from @pricing-strategy):
    - Free tier has smaller limits (handled by reverse-proxy/Nginx in production).
    """
    
    # 1. Generate Unique ID & File Paths (solves collision issue across internet users)
    job_id = str(uuid.uuid4())
    original_filename = file.filename
    clean_name, ext = os.path.splitext(original_filename)
    
    input_path = os.path.join(UPLOAD_DIR, f"{job_id}_{original_filename}")
    
    # Ensure the output filename includes the original video name as requested
    output_filename = f"{clean_name}_subbed.mkv"
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}_{output_filename}")
    
    # 2. Save the uploaded file to disk so FFmpeg can read it
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Free tier constraint: Limit to 3 mins
    duration = get_video_duration(input_path)
    if tier == "free" and duration > 180:
        os.remove(input_path)
        PROCESSING_JOBS[job_id] = {
            "status": "error",
            "error_message": "Free tier limit is reached. The transcription for the free tier should not in any case, whatsoever be more than 3 minutes."
        }
        return {
            "job_id": job_id, 
            "status": "processing", 
            "message": "Validating video duration..."
        }
        
    # 3. Queue the background task (solves timeout issue for long Whisper processes)
    background_tasks.add_task(process_video_job, job_id, input_path, output_path, tier, font, highlight_font)
    
    return {
        "job_id": job_id, 
        "status": "processing", 
        "message": "Video queued for AI transcription.",
        "marketing_prompt": "Did you know Pro users get priority queueing? Upgrade today!" # Up-sell CRO
    }

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Polling endpoint for the frontend to update the UI progress bar."""
    if job_id not in PROCESSING_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return PROCESSING_JOBS[job_id]

@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """
    Retrieve the finalized video block.
    In a real app, you would serve this using FastAPI FileResponse.
    """
    # For prototype, we just verify the file exists
    # Find the output file matching the job ID
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(job_id):
            output_path = os.path.join(OUTPUT_DIR, filename)
            # return FileResponse(path=output_path, filename=filename[len(job_id)+1:])
            return {"status": "ready", "file": filename[len(job_id)+1:], "path": output_path}
            
    raise HTTPException(status_code=404, detail="File processing not finished or file deleted.")

@app.get("/download_srt/{job_id}")
async def download_srt(job_id: str):
    """
    Retrieve the finalized .srt block specifically.
    """
    for filename in os.listdir(OUTPUT_DIR):
        if filename.startswith(job_id) and filename.endswith(".srt"):
            output_path = os.path.join(OUTPUT_DIR, filename)
            # return FileResponse(path=output_path, filename=filename[len(job_id)+1:])
            return {"status": "ready", "file": filename[len(job_id)+1:], "path": output_path}
            
    raise HTTPException(status_code=404, detail="SRT processing not finished or file deleted.")
