import streamlit as st
from transformers import pipeline
from gtts import gTTS
import uuid
import os

# --- Streamlit UI Config ---
st.set_page_config(page_title="EchoVerse", layout="wide")
st.markdown("""
    <style>
        .main { background-color: #f0f8ff; }
        h1, h2 { color: #4B0082; }
        .stButton > button { background-color: #6A5ACD; color: white; }
    </style>
""", unsafe_allow_html=True)
st.title("🎧 EchoVerse - AI-Powered Audiobook Generator")

# --- Load Hugging Face Model (Open Model: flan-t5-base) ---
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-base")

text_model = load_model()

# --- Rewriting Function ---
def rewrite_text(text, tone):
    prompts = {
        "Neutral": "Rewrite the following sentence in a neutral tone:",
        "Suspenseful": "Rewrite the following sentence to build suspense:",
        "Inspiring": "Rewrite the following sentence in an inspiring and motivational tone:"
    }
    full_prompt = f"{prompts[tone]} {text}"
    result = text_model(full_prompt, max_new_tokens=200, do_sample=True)
    return result[0]['generated_text'].strip()

# --- Generate Audio with gTTS ---
def generate_audio(text):
    os.makedirs("downloads", exist_ok=True)
    filename = f"downloads/{uuid.uuid4().hex}.mp3"
    tts = gTTS(text)
    tts.save(filename)
    return filename

# --- User Input ---
st.subheader("📝 Input Section")
user_text = st.text_area("Enter the text you want to convert to audio:", height=200)
tone_choice = st.selectbox("Choose a tone:", ["Neutral", "Suspenseful", "Inspiring"])

# --- Button to Rewrite and Narrate ---
if st.button("🔁 Rewrite & 🎤 Narrate"):
    if not user_text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("✍️ Rewriting the text..."):
            rewritten = rewrite_text(user_text, tone_choice)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Text")
            st.write(user_text)
        with col2:
            st.subheader(f"{tone_choice} Version")
            st.write(rewritten)

        with st.spinner("🔊 Generating narration..."):
            audio_file = generate_audio(rewritten)

        st.audio(audio_file, format="audio/mp3")
        with open(audio_file, "rb") as f:
            st.download_button("⬇️ Download Narration", f, file_name="echoverse_output.mp3", mime="audio/mp3")
