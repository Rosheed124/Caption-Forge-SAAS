import whisper
from whisper.utils import get_writer
import subprocess
import os
import sys
import time
import threading
import itertools


# --- 🔄 CUSTOM SPINNER CLASS ---
# This creates a professional animated loading sequence so you know it hasn't crashed!
class LoadingSpinner:
    def __init__(self, message="Loading..."):
        # The frames of our spinning animation
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay = 0.1
        self.busy = False
        self.message = message
        self.thread = None

    def spin(self):
        while self.busy:
            # \r forces the cursor to the start of the line so it overwrites itself cleanly
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(self.delay)
        # Clear the line when done
        sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
        sys.stdout.flush()

    def start(self):
        self.busy = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self, success_message="Done!"):
        self.busy = False
        time.sleep(self.delay)
        if self.thread:
            self.thread.join()
        print(f"✅ {success_message}")


def generate_and_burn_subtitles(video_path, output_video_path, font="Arial", highlight_font=None):
    print(f"\n--- 🎬 MSSN UI Auto-Subtitle Engine ---")
    combo_str = f"{font} + {highlight_font} (Highlight)" if highlight_font else font
    print(f"Processing File: {video_path} with Fonts: {combo_str}\n")

    # --- Step 1: Load the AI Model ---
    loader1 = LoadingSpinner("1. Loading Whisper AI Model...")
    loader1.start()
    model = whisper.load_model("base")
    loader1.stop("Whisper AI Model Loaded!")

    # --- Step 2: Transcribe the Audio ---
    # This is the longest step! The spinner will keep you sane.
    loader2 = LoadingSpinner("2. Listening and generating text... 🎧 (Grab a tea, this takes time for big videos)")
    loader2.start()
    result = model.transcribe(video_path)
    loader2.stop("Transcription Complete!")

    # --- Step 3: Create the .srt File ---
    loader3 = LoadingSpinner("3. Saving the .srt subtitle file...")
    loader3.start()
    input_dir = os.path.dirname(os.path.abspath(video_path)) or "."
    writer = get_writer("srt", input_dir)
    writer(result, video_path)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    original_srt_path = os.path.join(input_dir, f"{base_name}.srt")
    
    # Save SRT locally to the processed directory alongside our final video
    final_srt_path = output_video_path.replace(".mkv", ".srt").replace(".mp4", ".srt")
    os.rename(original_srt_path, final_srt_path)
    
    loader3.stop(f"Subtitles saved to: {final_srt_path}")

    # --- Step 4: Burn Subtitles into Video ---
    loader4 = LoadingSpinner("4. Burning subtitles into the final video... 🔥 (FFmpeg is rendering)")
    loader4.start()
    safe_srt_path = final_srt_path.replace("\\", "/")

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", f"subtitles='{safe_srt_path}':force_style='Fontname={font},FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2'",
        output_video_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    loader4.stop("Video rendering complete!")

    print(f"\n🎉 SUCCESS! Your subtitled video is ready: {output_video_path}\n")
    return os.path.basename(final_srt_path)


# --- CONFIGURATION (REMOVED FOR WEB SAAS) ---
# The backend FastAPI handles the unique file paths now.

if __name__ == "__main__":
    print("This module is now configured for Web SaaS usage via main.py")
    print("Run the server using: uvicorn main:app --reload")
