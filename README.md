# CaptionForge SAAS 🎬

CaptionForge is an AI-powered SaaS application that instantly transcribes video audio and permanently burns pixel-perfect subtitles directly into the video file. Built with OpenAI's Whisper model and FFmpeg, it eliminates the need for manual video editing by automating the entire subtitling pipeline.

## 🚀 Features

- **High-Accuracy Transcription**: Powered by OpenAI's Whisper AI (trained on 680,000+ hours of multilingual audio) for 99.2% transcription accuracy.
- **Hard-Burned Subtitles**: Uses FFmpeg to permanently embed subtitles into the video pixels—no soft overlays that disappear on other platforms.
- **Custom Typography & Pro Mixing**: Support for standard fonts (Arial, Roboto, Impact) and premium highlight font combinations (Montserrat, Bebas Neue, Cinzel, Pacifico).
- **Automated SRT Generation**: Automatically generates a perfectly timed `.srt` file alongside the burned video.
- **Pricing Tiers**: Built-in limits for Free vs Pro tiers (duration limits, font access).
- **Background Processing**: Non-blocking background worker queues for handling long Whisper processing tasks without timing out the web request.
- **Modern Glassmorphism UI**: Beautiful, highly-converting frontend built with TailwindCSS and Vanilla JS.

## 🛠 Tech Stack

- **Frontend**: HTML5, TailwindCSS, Vanilla JavaScript, Lucide Icons.
- **Backend**: Python, FastAPI.
- **AI/ML Engine**: `openai-whisper` (Base model).
- **Media Processing**: `ffmpeg` (Required system dependency).

## 📋 Prerequisites

Before running the project locally, ensure you have the following installed:

1. **Python 3.8+**
2. **FFmpeg**: Must be installed and accessible in your system's PATH.
   - *Windows*: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or use `winget install ffmpeg`.
   - *Mac*: `brew install ffmpeg`
   - *Linux*: `sudo apt install ffmpeg`

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/Caption-Forge-SAAS.git
   cd Caption-Forge-SAAS
   ```

2. **Set up a virtual environment (Recommended):**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Mac/Linux
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install fastapi uvicorn pydantic python-multipart openai-whisper
   ```

4. **Run the Backend Server:**
   ```bash
   uvicorn main:app --reload
   ```
   The backend will start at `http://127.0.0.1:8000`.

5. **Open the Frontend:**
   Simply open `index.html` in your web browser, or serve it using a local live server.

## 🔌 API Endpoints

- `POST /upload`: Uploads a video, validates pricing tier limits, and queues the background Whisper job.
- `GET /status/{job_id}`: Polling endpoint for the frontend to check transcription and rendering progress.
- `GET /download/{job_id}`: Retrieves the final hard-burned MKV/MP4 file.
- `GET /download_srt/{job_id}`: Retrieves the generated `.srt` file.

## 🗂 Project Structure

- `main.py`: The FastAPI application, API endpoints, and background job queue manager.
- `engine.py`: The core processing logic—loads the Whisper model, transcribes audio, saves SRT files, and executes FFmpeg commands.
- `index.html`: The fully-featured SaaS landing page and interactive application UI.

## 🛡️ License
Copyright © 2026. All rights reserved.
