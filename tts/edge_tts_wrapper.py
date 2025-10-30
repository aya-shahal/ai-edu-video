import os
import uuid
from elevenlabs import ElevenLabs, VoiceSettings, save

class ElevenLabsTTS:
    def __init__(self, api_key=None):
        self.client = ElevenLabs(api_key=api_key or os.getenv("ELEVEN_API_KEY"))
        # Fetch all available voices
        voices_response = self.client.voices.get_all()
        
        # The response is likely a wrapper object with a 'voices' attribute
        # Try to access the actual voices list
        if hasattr(voices_response, 'voices'):
            voices_data = voices_response.voices
        elif isinstance(voices_response, (list, tuple)):
            voices_data = list(voices_response)
        else:
            voices_data = [voices_response]
        
        if not voices_data:
            raise RuntimeError("No voices available in your ElevenLabs account.")
        
        # Build a dict {voice_name: voice_id}
        # Access voice properties correctly (might be attributes, not dict keys)
        self.available_voices = {}
        for v in voices_data:
            if hasattr(v, 'name') and hasattr(v, 'voice_id'):
                self.available_voices[v.name] = v.voice_id
            elif isinstance(v, dict):
                self.available_voices[v["name"]] = v["voice_id"]

    def generate_educational_speech(self, script_text, output_dir, voice_name=None):
        # Pick the requested voice, or default to first available
        if voice_name not in self.available_voices:
            print(f"WARNING: Voice '{voice_name}' not found. Using first available voice.")
            voice_name = next(iter(self.available_voices))
        voice_id = self.available_voices[voice_name]

        # Configure voice settings
        voice_settings = VoiceSettings(stability=0.8, similarity_boost=0.75)

        # Generate audio
        audio = self.client.text_to_speech.convert(
            voice_id=voice_id,
            text=script_text,
            model_id="eleven_monolingual_v1",
            voice_settings=voice_settings
        )

        # Save audio to file
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{uuid.uuid4().hex}.mp3")
        save(audio, output_file)
        return output_file

def generate_educational_speech(script_text, output_dir, voice_name=None):
    tts = ElevenLabsTTS()
    return tts.generate_educational_speech(script_text, output_dir, voice_name)

# Quick test
if __name__ == "__main__":
    tts = ElevenLabsTTS()
    print("Available voices:", list(tts.available_voices.keys()))
    file_path = tts.generate_educational_speech(
        "Hello! This is a test of ElevenLabs TTS.",
        output_dir="outputs",
        voice_name=None  # Will use first available
    )
    print("Generated audio at:", file_path)