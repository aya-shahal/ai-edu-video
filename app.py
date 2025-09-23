import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from llm.llm_wrapper import generate_script_api
from tts.edge_tts_wrapper import generate_educational_speech
from video.wav2lip_wrapper import Wav2LipGenerator

app = Flask(__name__)

# 📂 Folders
BASE_DIR = Path(os.getcwd())
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "mp4"}

wav2lip = Wav2LipGenerator(wav2lip_repo_path="Wav2Lip")

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload-face", methods=["POST"])
def upload_face():
    if "face" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})
    file = request.files["face"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"})
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file type"})
    filename = secure_filename(file.filename)
    save_path = UPLOAD_DIR / filename
    file.save(save_path)
    return jsonify({"success": True, "file_path": str(save_path)})

@app.route("/generate-script", methods=["POST"])
def generate_script():
    try:
        data = request.get_json()
        topic = data.get("topic", "").strip()
        face_path_str = data.get("face_path", "").strip()

        if not topic:
            return jsonify({"success": False, "error": "Please enter a topic"})

        # 1️⃣ Generate educational script
        script = generate_script_api(topic, duration_seconds=50, audience="high school")
        if script.startswith("Error:"):
            return jsonify({"success": False, "error": script})

        # 2️⃣ Generate TTS audio
        audio_path = generate_educational_speech(script, voice="jenny", output_dir=str(OUTPUT_DIR))
        if not audio_path:
            return jsonify({"success": False, "error": "TTS generation failed"})

        response = {
            "success": True,
            "script": script,
            "audio_url": f"/outputs/{Path(audio_path).name}"
        }

        # 3️⃣ Optional: Generate video if face is provided
        if face_path_str:
            face_path = Path(face_path_str)
            if face_path.exists():
                video_path = OUTPUT_DIR / "educational_video.mp4"
                video_result = wav2lip.generate_video(
                    face_image=str(face_path),
                    audio_file=str(audio_path),
                    output_path=str(video_path)
                )
                if video_result:
                    response["video_url"] = f"/outputs/{video_path.name}"
                else:
                    response["error"] = "Video generation failed"
            else:
                response["error"] = "Uploaded face file not found"

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {e}"})

@app.route("/outputs/<path:filename>")
def serve_outputs(filename):
    return send_from_directory(str(OUTPUT_DIR), filename)

if __name__ == "__main__":
    app.run(debug=True)
