import os
import uuid
import shutil
import threading
import logging
import traceback
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from deepface import DeepFace

from tts.edge_tts_wrapper import generate_educational_speech
from llm.llm_wrapper import generate_script_api
from sadtalker.sadtalker_wrapper import generate_educational_video

# ------------------ Logging ------------------
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s"
)

app = Flask(__name__)

# ------------------ Global ------------------
JOB_STATUSES = {}
BASE_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "presenters")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# ------------------ DeepFace ------------------
def detect_gender_from_image(image_path):
    try:
        analysis = DeepFace.analyze(
            img_path=image_path,
            actions=["gender"],
            enforce_detection=False
        )
        if not analysis:
            return "unknown"
        analysis = analysis[0]
        gender = analysis.get("dominant_gender", "").lower()
        if "woman" in gender or "female" in gender:
            return "female"
        if "man" in gender or "male" in gender:
            return "male"
        return "unknown"
    except Exception as e:
        logging.warning(f"DeepFace detection error: {e}")
        return "unknown"

# ------------------ Upload Presenter ------------------
@app.route("/upload-presenter", methods=["POST"])
def upload_presenter():
    try:
        if "presenter_image" not in request.files:
            return jsonify({"success": False, "error": "No image file provided"}), 400
        
        file = request.files["presenter_image"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
        file_path = os.path.join(IMAGES_DIR, filename)
        file.save(file_path)

        gender = detect_gender_from_image(file_path)
        logging.info(f"Image uploaded and gender detected: {gender}")

        suggested_voice = "guy" if gender == "male" else "jenny"
        return jsonify({
            "success": True,
            "filename": filename,
            "suggested_voice": suggested_voice,
            "gender": gender
        })
    except Exception as e:
        logging.error(f"Upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------ Background Video Generation ------------------
def background_video_generation(job_id, topic, source_image, voice):
    import time
    start_time = time.time()
    logging.info(f"[{job_id}] Starting video generation...")
    JOB_STATUSES[job_id] = {"status": "processing", "result": "Generating script..."}
    final_video_name = f"{job_id}.mp4"
    final_video_path = os.path.join(VIDEOS_DIR, final_video_name)

    try:
        # 1. Script
        logging.info(f"[{job_id}] Generating script for topic: {topic}")
        script = generate_script_api(topic, duration_seconds=60, audience="high school")
        if not script or len(script.strip()) < 10:
            raise Exception("Invalid script content")

        # 2. TTS
        JOB_STATUSES[job_id]["result"] = "Generating audio..."
        logging.info(f"[{job_id}] Generating audio with voice: {voice}")
        audio_path = generate_educational_speech(script_text=script, voice_name=voice, output_dir=OUTPUT_DIR)
        if not audio_path or not os.path.isfile(audio_path) or os.path.getsize(audio_path) < 1000:
            raise Exception("Audio generation failed or file too small")

        # 3. Validate image
        if not os.path.exists(source_image):
            raise Exception("Presenter image missing")

        # 4. Generate SadTalker Video
        JOB_STATUSES[job_id]["result"] = "Animating face..."
        logging.info(f"[{job_id}] Generating SadTalker video...")
        nested_video_path = generate_educational_video(audio_path, source_image, output_dir=VIDEOS_DIR)
        if not nested_video_path or not os.path.exists(nested_video_path):
            raise Exception("SadTalker video generation failed")

        shutil.move(nested_video_path, final_video_path)

        elapsed_time = time.time() - start_time
        JOB_STATUSES[job_id] = {"status": "complete", "result": f"/video/{final_video_name}", "elapsed_time": elapsed_time}
        logging.info(f"[{job_id}] Video generation complete: {final_video_path}")

    except Exception as e:
        elapsed_time = time.time() - start_time
        error_msg = f"Video generation failed: {e}"
        logging.error(f"[{job_id}] {error_msg}\n{traceback.format_exc()}")
        JOB_STATUSES[job_id] = {"status": "error", "result": error_msg, "elapsed_time": elapsed_time}

# ------------------ Endpoints ------------------
@app.route("/generate-video", methods=["POST"])
def generate_video():
    try:
        data = request.get_json(force=True)
        topic = data.get("topic")
        voice = data.get("voice", "jenny")
        presenter_image = data.get("presenter_image")

        if not topic or not presenter_image:
            return jsonify({"success": False, "error": "Missing topic or presenter image"}), 400

        source_image = os.path.join(IMAGES_DIR, presenter_image)
        if not os.path.exists(source_image):
            return jsonify({"success": False, "error": "Presenter image not found"}), 404

        job_id = str(uuid.uuid4())
        JOB_STATUSES[job_id] = {"status": "queued", "result": "Starting..."}

        threading.Thread(target=background_video_generation, args=(job_id, topic, source_image, voice), daemon=True, name=f"Job-{job_id[:8]}").start()
        logging.info(f"Job {job_id} queued for topic: {topic}")

        return jsonify({"success": True, "job_id": job_id})

    except Exception as e:
        logging.error(f"Generate-video error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/check-status/<job_id>", methods=["GET"])
def check_status(job_id):
    status = JOB_STATUSES.get(job_id)
    if not status:
        return jsonify({"status": "error", "result": "Job ID not found"}), 404
    return jsonify(status)

@app.route("/video/<path:filename>")
def serve_video(filename):
    return send_from_directory(VIDEOS_DIR, filename)

@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith(("/check-status", "/generate-video", "/upload-presenter", "/video/")):
        return jsonify({"status": "error", "message": "Invalid API path"}), 404
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health_check():
    active_jobs = len([j for j in JOB_STATUSES.values() if j["status"] == "processing"])
    total_jobs = len(JOB_STATUSES)
    return jsonify({"status": "healthy", "active_jobs": active_jobs, "total_jobs": total_jobs})

# ------------------ Run ------------------
if __name__ == "__main__":
    logging.info("🚀 Starting Educational Video Generator Server with ElevenLabs TTS")
    app.run(host="0.0.0.0", port=5057, debug=False, threaded=True)
