# app.py
from flask import Flask, render_template, request, jsonify
from llm.llm_wrapper import generate_script_api
import os

app = Flask(__name__)

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-script', methods=['POST'])
def generate_script():
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Please enter a topic'
            })
        
        # Generate script using your existing function with default values
        script = generate_script_api(
            topic=topic,
            duration_seconds=50,
            audience="high school"
        )
        
        # Check if script generation failed
        if script.startswith('Error:'):
            return jsonify({
                'success': False,
                'error': script
            })
        
        return jsonify({
            'success': True,
            'script': script,
            'topic': topic
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

if __name__ == '__main__':
    print("🎬 Educational Video Script Generator")
    print("📍 Running on: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    app.run(debug=True)