# tts/edge_tts_wrapper.py
import os
import asyncio
import hashlib
import edge_tts
from pathlib import Path

class EdgeTTSGenerator:
    """Edge TTS wrapper for educational video generation"""
    
    def __init__(self, default_voice="en-US-JennyNeural"):
        """
        Initialize Edge TTS Generator
        
        Args:
            default_voice (str): Default voice to use for speech generation
        """
        self.default_voice = default_voice
        
        # Educational-friendly voices
        self.educational_voices = {
            "jenny": "en-US-JennyNeural",      # Clear, friendly female
            "guy": "en-US-GuyNeural",          # Clear male voice
            "aria": "en-US-AriaNeural",        # Warm female voice
            "davis": "en-US-DavisNeural",      # Professional male
            "jane": "en-US-JaneNeural",        # Calm female voice
        }
    
    async def _generate_speech_async(self, text, output_path, voice):
        """Async method to generate speech"""
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            print(f"Edge TTS error: {e}")
            return None
    
    def generate_speech(self, text, output_path="output.wav", voice=None):
        """
        Generate speech from text using Edge TTS
        
        Args:
            text (str): Text to convert to speech
            output_path (str): Where to save the audio file
            voice (str): Voice to use (optional)
        
        Returns:
            str: Path to generated audio file or None if failed
        """
        if voice is None:
            voice = self.default_voice
        
        # If voice is a key, get the actual voice name
        if voice in self.educational_voices:
            voice = self.educational_voices[voice]
        
        try:
            result = asyncio.run(self._generate_speech_async(text, output_path, voice))
            if result:
                print(f"✅ Speech generated: {result}")
            return result
        except Exception as e:
            print(f"❌ Failed to generate speech: {e}")
            return None
    
    def generate_educational_speech(self, script_text, output_dir="outputs", voice="jenny"):
        """
        Generate speech optimized for educational content
        
        Args:
            script_text (str): Educational script from LLM
            output_dir (str): Directory to save audio files
            voice (str): Voice to use ('jenny', 'guy', 'aria', etc.)
        
        Returns:
            str: Path to generated audio file
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename based on script content
        script_hash = hashlib.md5(script_text.encode()).hexdigest()[:8]
        output_filename = f"educational_speech_{script_hash}.wav"
        output_path = os.path.join(output_dir, output_filename)
        
        # Clean up the script text
        cleaned_text = self._clean_script_for_speech(script_text)
        
        print(f"🔊 Generating educational speech with voice '{voice}'...")
        print(f"📝 Script preview: {cleaned_text[:100]}...")
        
        result = self.generate_speech(cleaned_text, output_path, voice)
        
        if result:
            # Get file info
            file_size = os.path.getsize(result) / 1024  # KB
            print(f"📊 Audio file: {file_size:.1f} KB")
            print(f"📁 Saved to: {os.path.abspath(result)}")
        
        return result
    
    def _clean_script_for_speech(self, script_text):
        """Clean script text for better speech synthesis"""
        # Remove extra whitespace
        cleaned = " ".join(script_text.split())
        
        # Add pauses for better pacing
        cleaned = cleaned.replace(". ", ". ")
        cleaned = cleaned.replace("! ", "! ")
        cleaned = cleaned.replace("? ", "? ")
        
        # Handle common abbreviations for better pronunciation
        replacements = {
            "AI": "A I",
            "ML": "M L",
            "GPU": "G P U",
            "CPU": "C P U",
            "API": "A P I",
            "URL": "U R L",
            "HTML": "H T M L",
            "CSS": "C S S",
        }
        
        for abbrev, pronunciation in replacements.items():
            cleaned = cleaned.replace(abbrev, pronunciation)
        
        return cleaned
    
    async def list_available_voices(self):
        """List available voices for educational content"""
        try:
            voices = await edge_tts.list_voices()
            
            print("\n🎙️ Available voices for educational content:")
            print("=" * 50)
            
            # Filter English voices
            en_voices = [v for v in voices if v['Locale'].startswith('en-US')]
            
            for key, voice_id in self.educational_voices.items():
                voice_info = next((v for v in en_voices if v['ShortName'] == voice_id), None)
                if voice_info:
                    gender = voice_info.get('Gender', 'Unknown')
                    print(f"  {key:8} -> {voice_info['FriendlyName']} ({gender})")
            
            print("\nUsage: generate_educational_speech(text, voice='jenny')")
            
        except Exception as e:
            print(f"Could not list voices: {e}")


# Convenience functions for easy integration
def generate_educational_speech(script_text, voice="jenny", output_dir="outputs"):
    """
    Easy-to-use function to generate educational speech
    
    Args:
        script_text (str): Educational script
        voice (str): Voice name ('jenny', 'guy', 'aria', etc.)
        output_dir (str): Output directory
    
    Returns:
        str: Path to generated audio file
    """
    tts = EdgeTTSGenerator()
    return tts.generate_educational_speech(script_text, output_dir, voice)


def list_voices():
    """List available educational voices"""
    tts = EdgeTTSGenerator()
    asyncio.run(tts.list_available_voices())


# Test function
async def test_edge_tts():
    """Test Edge TTS with educational content"""
    test_script = """
    Welcome to today's lesson about artificial intelligence. 
    A I is a rapidly growing field that focuses on creating machines that can think and learn like humans.
    In this video, we'll explore the basics of machine learning and neural networks.
    By the end of this lesson, you'll understand how computers can recognize patterns and make predictions.
    """
    
    tts = EdgeTTSGenerator()
    
    print("Testing different educational voices...")
    
    # Test different voices
    for voice_name in ["jenny", "guy", "aria"]:
        print(f"\n🎙️ Testing voice: {voice_name}")
        result = tts.generate_educational_speech(
            test_script.strip(), 
            output_dir="test_outputs",
            voice=voice_name
        )
        
        if result:
            print(f"✅ Generated: {result}")
        else:
            print(f"❌ Failed to generate with {voice_name}")


if __name__ == "__main__":
    print("Edge TTS Educational Voice Generator")
    print("=" * 40)
    
    # List available voices
    list_voices()
    
    # Run test
    print("\nRunning test...")
    asyncio.run(test_edge_tts())