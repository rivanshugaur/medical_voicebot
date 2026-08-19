import os
import asyncio
import edge_tts
from dotenv import load_dotenv

load_dotenv()

async def _generate_speech(input_text, output_filepath):
    # Using a clear, AI-sounding robotic voice provided by Edge-TTS (much better than gTTS, free alternative to ElevenLabs)
    communicate = edge_tts.Communicate(input_text, "en-US-GuyNeural")
    await communicate.save(output_filepath)

def text_to_speech_with_gtts(input_text, output_filepath):
    """
    Despite the name keeping compatibility with existing code, 
    this uses edge-tts for a high-quality free voice generation.
    """
    try:
        asyncio.run(_generate_speech(input_text, output_filepath))
    except Exception as e:
        print(f"An error occurred while generating TTS: {e}")

if __name__ == "__main__":
    # Test
    text_to_speech_with_gtts("Hi this is a test of the robotic voice.", "edge_testing.mp3")
