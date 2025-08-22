from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil, os, cv2
import easyocr
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/process")
async def process_video(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    video = VideoFileClip(input_path)
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)

    reader = easyocr.Reader(["en"])
    scoreboard_region = (50, 20, 250, 100)  # Adjust to your broadcast
    prev_score = None
    events = []

    for t in range(0, duration, 2):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if not ret:
            continue

        x, y, w, h = scoreboard_region
        crop = frame[y:y+h, x:x+w]
        results = reader.readtext(crop)
        detected_text = " ".join([res[1] for res in results]).strip()

        if "-" in detected_text or ":" in detected_text:
            score = detected_text.replace(":", "-")
            if prev_score and score != prev_score:
                start = max(0, t - 10)
                end = min(duration, t + 15)
                events.append((start, end))
                prev_score = score
            else:
                prev_score = score

    cap.release()

    clips = [video.subclip(start, end) for start, end in events]

    def add_overlay(clip, text):
        txt = (TextClip(text, fontsize=60, color="yellow", font="Arial-Bold")
               .set_position(("center","bottom"))
               .set_duration(clip.duration))
        return CompositeVideoClip([clip, txt])

    highlight_clips = [add_overlay(c, "⚽ GOAL!") for c in clips]

    if not highlight_clips:
        highlight_clips = [video.subclip(0, min(60, video.duration))]  # fallback

    final = concatenate_videoclips(highlight_clips, method="compose")
    if final.duration > 180:
        final = final.subclip(0, 180)

    output_path = os.path.join(OUTPUT_DIR, "highlight.mp4")
    final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)

    return FileResponse(output_path, media_type="video/mp4", filename="kglai_highlights.mp4")
