import os
import logging
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def transcribe_with_groq(GROQ_API_KEY, audio_filepath, stt_model="whisper-large-v3"):
    client = Groq(api_key=GROQ_API_KEY)

    try:
        audio_file = open(audio_filepath, "rb")
        transcription = client.audio.transcriptions.create(
            model=stt_model,
            file=audio_file,
            language="en"
        )
        return transcription.text
    except Exception as e:
        logging.error(f"Error in transcription: {e}")
        raise e
    finally:
        # Make sure to close the file
        if 'audio_file' in locals() and audio_file:
            audio_file.close()