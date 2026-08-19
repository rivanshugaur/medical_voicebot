# Medical VoiceBot

An AI Doctor with Vision and Voice.
Upload a medical image, ask your question via voice, and get an AI analysis spoken back to you in a clear, robotic/AI voice.

## How to run locally

1. Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

## How to deploy on Streamlit Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and create a new app.
3. Select your repository and set the main file path to `app.py`.
4. In the "Advanced settings" (or App Settings -> Secrets), add your Groq API key:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```
5. Click **Deploy!**

The app is fully oriented for Streamlit Cloud:
- Native `st.audio_input` for streamable microphone recording.
- Uses `edge-tts` for high-quality, free robotic/AI-like voice generation (no API key needed).
- Removes problematic system dependencies like PyAudio/SpeechRecognition, using raw audio chunks for Groq STT directly.
