import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
load_dotenv()

from voicebot import analyze_image_with_query, encode_image
from response import text_to_speech_with_gtts
from record_voice import transcribe_with_groq

system_prompt = """
You are a medical image assistant.

Analyze the medical image and answer the user's spoken question.

Give a short, natural answer in plain English, like a doctor speaking to a patient.

Rules:
- Maximum 2 short sentences.
- Directly answer the user's question.
- If the image appears normal, clearly say that it appears normal.
- If you notice a possible abnormality, briefly explain it.
- Do not use Markdown.
- Do not use asterisks.
- Do not use headings.
- Do not use bullet points.
- Do not give a detailed medical report.
- Do not list multiple possibilities unless necessary.
- Do not start with a preamble.
- Do not claim certainty or give a definitive diagnosis.
"""

st.set_page_config(page_title="AI Doctor with Vision and Voice", layout="centered")

st.title("🤖 AI Doctor with Vision and Voice")
st.markdown("Upload a medical image and record your question to get an AI analysis with voice response.")

# 1. Image Upload
uploaded_image = st.file_uploader("1. Upload Medical Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

# 2. Audio Input (Streamable native Streamlit audio input)
st.markdown("### 2. Record your question")
audio_value = st.audio_input("Record your voice")

if audio_value is not None:
    # Process the audio once recorded
    with st.spinner("Transcribing your question..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_value.getvalue())
            temp_audio_path = temp_audio.name
            
        try:
            speech_to_text_output = transcribe_with_groq(
                GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
                audio_filepath=temp_audio_path,
                stt_model="whisper-large-v3"
            )
            st.success(f"**You asked:** {speech_to_text_output}")
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")
            speech_to_text_output = None
        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            
    if speech_to_text_output:
        with st.spinner("Analyzing image and generating response..."):
            if uploaded_image:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
                    temp_image.write(uploaded_image.getvalue())
                    temp_image_path = temp_image.name
                
                try:
                    doctor_response = analyze_image_with_query(
                        query=speech_to_text_output,
                        system_prompt=system_prompt,
                        encoded_image=encode_image(temp_image_path),
                        model="qwen/qwen3.6-27b" # Note: Groq model name, adjust if changed
                    )
                    import re
                    doctor_response = re.sub(r'<think>.*?</think>', '', doctor_response, flags=re.DOTALL).strip()
                except Exception as e:
                    doctor_response = f"Error analyzing image: {e}"
                finally:
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
            else:
                doctor_response = "No image provided for me to analyze. " + speech_to_text_output
            
            st.info(f"**Doctor's Response:** {doctor_response}")
            
        with st.spinner("Generating audio response..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_out_audio:
                output_audio_path = temp_out_audio.name
                
            try:
                # Generate TTS
                text_to_speech_with_gtts(input_text=doctor_response, output_filepath=output_audio_path)
                
                # Read the generated audio and play it on frontend
                with open(output_audio_path, "rb") as f:
                    audio_bytes = f.read()
                
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.error(f"Error generating TTS: {e}")
            finally:
                if os.path.exists(output_audio_path):
                    os.remove(output_audio_path)
