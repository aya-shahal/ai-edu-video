# 🧠 AI Educational Video Generator

## 🎯 Problem Statement
Creating high-quality educational videos requires scripting, voice recording, and manual animation — a process that’s time-consuming and expensive.  
This project automates the entire pipeline using **AI models** that generate scripts, synthesize voices, and animate human avatars with lip-sync — turning text into an educational video in minutes.

---

## ⚙️ Tech Stack

| Component | Purpose | Library / Model |
|------------|----------|----------------|
| **Script Generation** | Automatically writes educational content or explanations | 🦙 **LLaMA** |
| **Text-to-Speech** | Converts AI-generated script into natural-sounding speech | 🗣️ **Edge-TTS** |
| **Face Detection & Gender Recognition** | Detects face and gender for accurate rendering setup | 👤 **FaceRender** |
| **Lip-Sync Animation** | Generates realistic talking-head animation synced with speech | 🎬 **SadTalker** |

---

## 🧩 Architecture Overview

Input Topic  →  LLaMA →  Script Text  
↓  
Edge-TTS →  Audio (WAV)  
↓  
FaceRender →  Face & Gender Detection  
↓  
SadTalker →  Lip-Synced Video Output  

Final output: a fully generated **AI educational video** with synced facial animation and voice narration.

---

## 🚀 How to Run

### 1. Clone the Repository
git clone https://github.com/your-username/ai-educational-video.git  
cd ai-educational-video  

### 2. Create & Activate a Virtual Environment
python -m venv venv  
source venv/bin/activate   # (Linux/macOS)  
venv\Scripts\activate      # (Windows)  

### 3. Install Dependencies
pip install -r requirements.txt  

### 4. Setup SadTalker
SadTalker is used for lip-sync animation. Follow these steps:

# Clone SadTalker repository  
git clone https://github.com/OpenTalker/SadTalker.git  
cd SadTalker  

# Create and activate a virtual environment  
python -m venv venv  
source venv/bin/activate   # (Linux/macOS)  
venv\Scripts\activate      # (Windows)  

# Install required packages  
pip install -r requirements.txt  

# Download checkpoints  
bash scripts/download_models.sh  

Once the models are downloaded successfully, you can integrate SadTalker into your main pipeline.

---

### 5. Run the Full Pipeline
From the main project folder:
python app.py 

### 6. Output
- 🧾 output/script.txt — AI-generated educational script  
- 🔊 output/audio.wav — TTS narration  
- 🎥 output/video.mp4 — Final lip-synced educational video  

---

## 🔮 Future Improvements
- Multi-language voice synthesis  
- Emotion-aware facial animation  
- Background and subtitle generation  
- Integration with educational content APIs  
