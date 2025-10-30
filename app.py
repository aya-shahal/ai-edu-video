from flask import Flask, render_template, request, jsonify, send_from_directory
from llm.llm_wrapper import generate_script_api
from tts.edge_tts_wrapper import generate_educational_speech
from sadtalker.sadtalker_wrapper import generate_educational_video
import os

app = Flask(__name__)

# ---- Output directories ----
BASE_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "presenters")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


@app.route("/")
def home():
    # Make sure you have a templates/index.html file
    return render_template("index.html")


@app.route("/generate-script", methods=["POST"])
def generate_script():
    try:
        data = request.get_json(force=True)
        topic = data.get("topic", "").strip()
        if not topic:
            return jsonify({"success": False, "error": "Please enter a topic"})

        # 1️⃣ Generate LLM script
        script = generate_script_api(topic, duration_seconds=50, audience="high school")
        if script.startswith("Error:"):
            return jsonify({"success": False, "error": script})

        # 2️⃣ Generate audio
        audio_path = generate_educational_speech(
            script, voice="jenny", output_dir=OUTPUT_DIR
        )
        if not audio_path:
            return jsonify({"success": False, "error": "TTS generation failed"})

        return jsonify(
            {
                "success": True,
                "script": script,
                "audio_url": f"/audio/{os.path.basename(audio_path)}",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/generate-video", methods=["POST"])
def generate_video():
    try:
        data = request.get_json(force=True)
        topic = data.get("topic", "").strip()
        presenter_image = data.get("presenter_image", None)

        if not topic:
            return jsonify({"success": False, "error": "Please enter a topic"})

        # 1️⃣ Script + Audio
        script = generate_script_api(topic, duration_seconds=50, audience="high school")
        audio_path = generate_educational_speech(
            script, voice="jenny", output_dir=OUTPUT_DIR
        )

        # 2️⃣ Source image (presenter)
        source_image = None
        if presenter_image:
            img_path = os.path.join(IMAGES_DIR, presenter_image)
            if os.path.exists(img_path):
                source_image = img_path
            else:
                return jsonify({"success": False, "error": "Presenter image not found"})

        # 3️⃣ Generate video with SadTalker
        video_path = generate_educational_video(
            audio_path=audio_path,
            image_path=source_image,  # ✅ matches sadtalker_wrapper argument
            output_dir=VIDEOS_DIR
        )

        if not video_path or not os.path.exists(video_path):
            return jsonify({"success": False, "error": "Video generation failed"})

        return jsonify(
            {
                "success": True,
                "script": script,
                "audio_url": f"/audio/{os.path.basename(audio_path)}",
                "video_url": f"/video/{os.path.basename(video_path)}",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/upload-presenter", methods=["POST"])
def upload_presenter():
    try:
        if "presenter_image" not in request.files:
            return jsonify({"success": False, "error": "No image file provided"})

        file = request.files["presenter_image"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"})

        filename = f"custom_{file.filename}"
        file_path = os.path.join(IMAGES_DIR, filename)
        file.save(file_path)

        return jsonify({"success": True, "filename": filename})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/list-presenters")
def list_presenters():
    try:
        files = [
            f for f in os.listdir(IMAGES_DIR)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        return jsonify({"success": True, "presenters": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ---- Serve static files ----
@app.route("/audio/<path:filename>")
def serve_audio(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route("/video/<path:filename>")
def serve_video(filename):
    return send_from_directory(VIDEOS_DIR, filename)

@app.route("/presenter/<path:filename>")
def serve_presenter(filename):
    return send_from_directory(IMAGES_DIR, filename)


if __name__ == "__main__":
    print("🚀 Starting Educational Video Generator")
    # Use 0.0.0.0 if you want to access externally (e.g. LAN)
    app.run(host="0.0.0.0", port=5050, debug=True)
