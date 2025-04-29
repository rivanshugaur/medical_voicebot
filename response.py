#if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

#Step1a: Setup Text to Speech–TTS–model with gTTS
import os
from gtts import gTTS



#Step2: Use Model for Text output to Voice

import subprocess
import platform

def text_to_speech_with_gtts(input_text, output_filepath):
    language="en"

    audioobj= gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            # Windows Media.SoundPlayer only supports WAV files, not MP3
            # Convert MP3 to WAV if the file is MP3
            if output_filepath.lower().endswith('.mp3'):
                from pydub import AudioSegment
                wav_filepath = output_filepath.replace('.mp3', '.wav')
                AudioSegment.from_mp3(output_filepath).export(wav_filepath, format="wav")
                # Use the converted WAV file
                subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_filepath}").PlaySync();'])
            else:
                subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])  # Alternative: use 'mpg123' or 'ffplay'
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")


input_text="Hi this is Navneet, autoplay testing!"
#text_to_speech_with_gtts(input_text=input_text, output_filepath="gtts_testing_autoplay.mp3")


