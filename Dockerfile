# Base image: NVIDIA CUDA 12.1.1 runtime with Ubuntu 22.04
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# -----------------------------------------------------------------------------
# 1. System dependencies
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    python3 python3-pip git ffmpeg libgl1 wget build-essential cmake libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# 2. Working directory
# -----------------------------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------------------------
# 3. Copy application files
# -----------------------------------------------------------------------------
COPY app.py requirements.txt /app/
COPY sadtalker/ /app/sadtalker/
COPY llm/ /app/llm/
COPY tts/ /app/tts/
COPY templates/ /app/templates/

# -----------------------------------------------------------------------------
# 4. Upgrade pip and install core build tools
# -----------------------------------------------------------------------------
RUN python3 -m pip install --upgrade pip setuptools wheel

# -----------------------------------------------------------------------------
# 5. Install pre-built dlib wheel (avoids compilation failure on Render)
# -----------------------------------------------------------------------------
RUN python3 -m pip install dlib==19.24.0

# -----------------------------------------------------------------------------
# 6. Install PyTorch stack (CUDA 12.1 compatible + SadTalker safe)
# -----------------------------------------------------------------------------
RUN python3 -m pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cu121

# -----------------------------------------------------------------------------
# 7. Install general and SadTalker dependencies
# -----------------------------------------------------------------------------
RUN python3 -m pip install -r requirements.txt
RUN if [ -f /app/sadtalker/requirements.txt ]; then python3 -m pip install -r /app/sadtalker/requirements.txt; fi

# -----------------------------------------------------------------------------
# 8. DeepFace + TensorFlow (CPU fallback only)
# -----------------------------------------------------------------------------
RUN python3 -m pip install deepface==0.0.91 tensorflow==2.11.0 protobuf==3.19.0
RUN python3 -m pip install elevenlabs==1.8.1

# -----------------------------------------------------------------------------
# 9. Transformer stack (compatible with PyTorch 2.0+)
# -----------------------------------------------------------------------------
RUN python3 -m pip install transformers==4.41.2

# -----------------------------------------------------------------------------
# 10. Environment configuration
# -----------------------------------------------------------------------------
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/huggingface_cache \
    TRANSFORMERS_CACHE=/app/huggingface_cache \
    MODEL_DIR=/app/models

# -----------------------------------------------------------------------------
# 11. Create cache/model directories
# -----------------------------------------------------------------------------
RUN mkdir -p ${HF_HOME} ${MODEL_DIR}

# -----------------------------------------------------------------------------
# 12. Expose port and run Flask app via Gunicorn
# -----------------------------------------------------------------------------
EXPOSE 5054
CMD ["gunicorn", "--bind", "0.0.0.0:5054", "app:app", "--workers", "2", "--threads", "2", "--timeout", "600"]
