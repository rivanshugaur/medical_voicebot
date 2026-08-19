import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
load_dotenv()

from voicebot import analyze_image_with_query, encode_image
from response import text_to_speech_with_gtts
from record_voice import transcribe_with_groq

system_prompt = """
You are a highly knowledgeable, empathetic, and helpful medical image assistant.

Analyze the medical image and answer the user's spoken question thoughtfully.

Give a clear, natural, and comprehensive answer in plain English, as if you are a caring doctor explaining things to a patient.

Rules:
- Provide helpful, actionable advice and context. Elaborate on the condition, possible causes, and general recommended care or over-the-counter options.
- ALWAYS emphasize that you are an AI and they should consult a real dermatologist or doctor for a formal diagnosis.
- Speak in a natural, conversational tone since your output will be converted to speech.
- Avoid using complex Markdown, bullet points, asterisks, or headings because those do not sound good when read aloud by text-to-speech.
- Directly answer the user's specific question based on the image provided.
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
            groq_key = os.environ.get("GROQ_API_KEY")
            if not groq_key:
                st.error("GROQ_API_KEY is not set. Please add it to Streamlit Cloud Settings > Secrets.")
                speech_to_text_output = None
            else:
                speech_to_text_output = transcribe_with_groq(
                    GROQ_API_KEY=groq_key,
                    audio_filepath=temp_audio_path,
                    stt_model="whisper-large-v3"
                )
                if speech_to_text_output and speech_to_text_output.strip():
                    st.success(f"**You asked:** {speech_to_text_output}")
                else:
                    st.warning("Could not hear any speech. Please try recording again.")
                    speech_to_text_output = None
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
                        model="qwen/qwen3.6-27b", # Note: Groq model name, adjust if changed
                        GROQ_API_KEY=groq_key
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
