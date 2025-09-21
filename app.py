# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
from llm.llm_wrapper import generate_script_api
from tts.edge_tts_wrapper import generate_educational_speech   # ✅ IMPORT
import os

app = Flask(__name__)

# Make sure an outputs folder exists (to serve audio files)
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-script', methods=['POST'])
def generate_script():
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()

        if not topic:
            return jsonify({'success': False, 'error': 'Please enter a topic'})

        # 1️⃣ Generate text
        script = generate_script_api(topic, duration_seconds=50, audience="high school")
        if script.startswith('Error:'):
            return jsonify({'success': False, 'error': script})

        # 2️⃣ Generate speech
        audio_path = generate_educational_speech(script, voice="jenny", output_dir=OUTPUT_DIR)
        if not audio_path:
            return jsonify({'success': False, 'error': 'TTS generation failed'})

        # 3️⃣ Return relative filename to serve later
        filename = os.path.basename(audio_path)
        return jsonify({
            'success': True,
            'script': script,
            'audio_url': f'/audio/{filename}'   # client can <audio src="">
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

# ✅ Route to serve audio files
@app.route('/audio/<path:filename>')
def audio(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
