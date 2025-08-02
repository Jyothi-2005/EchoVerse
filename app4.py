import streamlit as st
from transformers import pipeline
from gtts import gTTS
import uuid
import os
import PyPDF2
from io import BytesIO

# --- Streamlit UI Config ---
st.set_page_config(
    page_title="EchoVerse - AI Audiobook Generator", 
    layout="wide",
    page_icon="🎧"
)

# Enhanced CSS with light blue, white, and pink color scheme
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        .main {
            background: linear-gradient(135deg, #e3f2fd 0%, #f8bbd9 50%, #ffffff 100%);
            font-family: 'Poppins', sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #e3f2fd 0%, #f8bbd9 50%, #ffffff 100%);
        }
        
        h1 {
            color: #1565c0;
            text-align: center;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        h2, h3 {
            color: #ad1457;
            font-weight: 600;
        }
        
        .stButton > button {
            background: linear-gradient(45deg, #42a5f5, #ec407a);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        .stSelectbox > div > div {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            border: 2px solid #81d4fa;
        }
        
        .stTextArea > div > div > textarea {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            border: 2px solid #81d4fa;
            color: #1565c0;
        }
        
        .upload-section {
            background: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 15px;
            border: 2px dashed #42a5f5;
            margin: 20px 0;
            text-align: center;
        }
        
        .text-display {
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #ec407a;
            margin: 10px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.9);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 15px 0;
            border-top: 4px solid #42a5f5;
        }
        
        .stSuccess {
            background-color: rgba(76, 175, 80, 0.1);
            border-left: 5px solid #4caf50;
        }
        
        .stWarning {
            background-color: rgba(255, 193, 7, 0.1);
            border-left: 5px solid #ffc107;
        }
        
        .stInfo {
            background-color: rgba(33, 150, 243, 0.1);
            border-left: 5px solid #2196f3;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #e1f5fe, #fce4ec);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title with animated emoji ---
st.markdown("""
    <h1>🎧 EchoVerse - AI-Powered Audiobook Generator ✨</h1>
    <p style='text-align: center; color: #666; font-size: 18px; margin-bottom: 30px;'>
        Transform your text into captivating audio experiences with AI-powered rewriting and natural voice synthesis
    </p>
""", unsafe_allow_html=True)

# --- Load Hugging Face Model (Open Model: flan-t5-base) ---
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-base")

text_model = load_model()

# --- File processing functions ---
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_txt(txt_file):
    """Extract text from TXT file"""
    try:
        return str(txt_file.read(), "utf-8")
    except Exception as e:
        st.error(f"Error reading text file: {str(e)}")
        return None

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

# --- Main Interface ---

st.subheader("📝 Input Your Content")

# Tab interface for different input methods
tab1, tab2 = st.tabs(["✍ Type Text", "📁 Upload File"])

# Initialize variables
manual_text = ""
uploaded_text = ""

with tab1:
    manual_text = st.text_area(
        "Enter the text you want to convert to audio:", 
        height=200,
        placeholder="Type or paste your text here...",
        key="manual_text_input"
    )

with tab2:
    st.markdown("### 📎 Upload Text File")
    st.markdown("Supported formats: *TXT, **PDF*")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'pdf'],
        help="Upload a text file (.txt) or PDF file (.pdf)"
    )
    
    if uploaded_file is not None:
        file_type = uploaded_file.type
        
        with st.spinner("📖 Processing your file..."):
            if file_type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            elif file_type == "text/plain":
                extracted_text = extract_text_from_txt(uploaded_file)
            else:
                st.error("Unsupported file type!")
                extracted_text = None
        
        if extracted_text:
            uploaded_text = extracted_text
            st.success(f"✅ File processed successfully! Extracted {len(extracted_text)} characters.")
            
            # Show preview of extracted text
            with st.expander("👀 Preview Extracted Text"):
                st.text_area("File Content Preview:", value=extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text, height=150, disabled=True)

# Determine which text to use - prioritize manual text if both exist
final_text = manual_text if manual_text.strip() else uploaded_text

# Tone selection
st.subheader("🎨 Customization")
tone_choice = st.selectbox(
    "Choose a tone:", 
    ["Neutral", "Suspenseful", "Inspiring"],
    help="Select how you want your text to be rewritten"
)

# Add some metrics/info
if final_text and final_text.strip():
    col_met1, col_met2 = st.columns(2)
    with col_met1:
        st.metric("📊 Characters", len(final_text))
    with col_met2:
        st.metric("📝 Words", len(final_text.split()))

st.markdown('</div>', unsafe_allow_html=True)

# --- Processing Section ---

st.subheader("🚀 Generate Your Audiobook")

# Get the current text value
current_text = final_text

# Enhanced button with better styling
if st.button("🔁 Rewrite & 🎤 Narrate", key="main_button"):
    if not current_text or not current_text.strip():
        st.warning("⚠ Please enter some text or upload a file first.")
    else:
        # Progress bar for better UX
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Rewriting
        status_text.text("✍ AI is rewriting your text...")
        progress_bar.progress(25)
        
        with st.spinner("🤖 AI is working its magic..."):
            rewritten = rewrite_text(current_text, tone_choice)
        
        progress_bar.progress(50)
        
        # Step 2: Display results
        status_text.text("📝 Displaying results...")
        progress_bar.progress(75)
        
        col1, col2 = st.columns(2)
        
        with col1:
           
            st.subheader("📄 Original Text")
            st.write(current_text)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
        
            st.subheader(f"✨ {tone_choice} Version")
            st.write(rewritten)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 3: Generate audio
        status_text.text("🔊 Generating narration...")
        progress_bar.progress(90)
        
        with st.spinner("🎵 Creating your audiobook..."):
            audio_file = generate_audio(rewritten)
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        
        # Audio player with enhanced styling
        st.markdown("### 🎧 Your Generated Audiobook")
        st.audio(audio_file, format="audio/mp3")
        
        # Download button
        with open(audio_file, "rb") as f:
            st.download_button(
                "⬇ Download Narration", 
                f, 
                file_name="echoverse_output.mp3", 
                mime="audio/mp3",
                help="Click to download your generated audiobook"
            )
        
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success("🎉 Your audiobook has been generated successfully!")

st.markdown('</div>', unsafe_allow_html=True)

# --- Footer with features ---
st.markdown("---")
st.markdown("### ✨ Why Choose EchoVerse?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    *🤖 AI-Powered*  
    Advanced text rewriting using state-of-the-art language models
    """)

with col2:
    st.markdown("""
    *📁 Multi-Format*  
    Support for TXT and PDF file uploads for easy content processing
    """)

with col3:
    st.markdown("""
    *🎨 Customizable*  
    Multiple tone options to match your desired narrative style
    """)