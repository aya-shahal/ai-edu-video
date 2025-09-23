import os
import subprocess
from pathlib import Path

class Wav2LipGenerator:
    """
    Wrapper for Wav2Lip to generate talking head videos
    from a single image and an audio file.
    """

    def __init__(self, wav2lip_repo_path="Wav2Lip"):
        self.repo_path = Path(wav2lip_repo_path)
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Wav2Lip repo not found at {self.repo_path}. Clone it from GitHub.")

        self.model_path = self.repo_path / "checkpoints" / "wav2lip.pth"
        if not self.model_path.exists():
            raise FileNotFoundError(f"Wav2Lip model not found at {self.model_path}. Download it from the repo instructions.")

    def generate_video(self, face_image, audio_file, output_path="outputs/output_video.mp4"):
        """
        Generate talking head video from an image and audio.
        """

        # ✅ Convert everything to absolute paths
        face_image = os.path.abspath(face_image)
        audio_file = os.path.abspath(audio_file)
        output_path = os.path.abspath(output_path)

        Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
        
        # ✅ Ensure temp directory exists in Wav2Lip folder
        temp_dir = self.repo_path / "temp"
        temp_dir.mkdir(exist_ok=True)

        # ✅ Use relative paths from Wav2Lip directory perspective
        command = [
            "python3",
            "inference.py",
            "--checkpoint_path", "checkpoints/wav2lip.pth",
            "--face", face_image,
            "--audio", audio_file,
            "--outfile", output_path
        ]

        try:
            # ✅ KEY FIX: Change working directory to Wav2Lip folder
            result = subprocess.run(
                command, 
                cwd=str(self.repo_path),  # This is the crucial fix!
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ Video generated at {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Wav2Lip failed: {e}")
            print(f"❌ STDOUT: {e.stdout}")
            print(f"❌ STDERR: {e.stderr}")
            return None