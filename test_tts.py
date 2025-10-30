import asyncio
import edge_tts

async def main():
    text = "Hello world!"
    voice = "en-US-GuyNeural"
    output = "test_audio.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)
    print("✅ Done:", output)

asyncio.run(main())
