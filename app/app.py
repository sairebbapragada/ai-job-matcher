import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
import re
from docx import Document
from scipy.io.wavfile import write
import tempfile

# ------------------------------
# LOAD API KEY
# ------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ API key missing")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------------------------
# PDF READER
# ------------------------------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ------------------------------
# SCORE EXTRACTOR
# ------------------------------
def extract_score(text):
    match = re.search(r"\b(\d{1,3})\b", text)
    if match:
        return min(int(match.group(1)), 100)
    return 50

# ------------------------------
# RESUME REWRITE
# ------------------------------
def rewrite_resume(resume_text, job_desc):
    prompt = f"""
Rewrite this resume using SAME structure:
- Summary
- Education
- Experience
- Skills

Improve wording, make it ATS-friendly, tailor to job.

Resume:
{resume_text}

Job:
{job_desc}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ------------------------------
# WORD EXPORT
# ------------------------------
def create_word_doc(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    return doc

# ------------------------------
# MOCK INTERVIEW
# ------------------------------
def mock_interview(history, resume_text):
    prompt = f"""
You are a professional interviewer.

Resume:
{resume_text}

Conversation:
{history}

Ask the NEXT interview question only.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ------------------------------
# VOICE RECORDING
# ------------------------------
def record_audio():
    fs = 44100
    seconds = 5

    st.info("🎤 Recording...")
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_file.name, fs, recording)

    return temp_file.name

# ------------------------------
# UI
# ------------------------------
st.set_page_config(page_title="AI Career Assistant", layout="wide")

st.title("🚀 AI Career Assistant")

col1, col2 = st.columns(2)

# Resume upload
with col1:
    st.subheader("📄 Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    resume_text = ""
    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)
        st.success("Resume uploaded!")

# Job description
with col2:
    st.subheader("💼 Job Description")
    job_desc = st.text_area("Paste job description")

# ------------------------------
# MATCHING
# ------------------------------
if st.button("🎯 Match Resume to Job"):
    if resume_text and job_desc:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
Compare resume and job.

Give:
- Match score
- Missing skills
- Suggestions

Resume:
{resume_text}

Job:
{job_desc}
"""
            }]
        )

        result = response.choices[0].message.content

        st.write(result)

        score = extract_score(result)
        st.progress(score)
        st.success(f"Match Score: {score}%")
    else:
        st.warning("Upload resume + paste job")

# ------------------------------
# RESUME IMPROVER
# ------------------------------
if st.button("✍️ Improve Resume"):
    if resume_text:
        improved = rewrite_resume(resume_text, job_desc)

        st.text_area("Improved Resume", improved, height=400)

        doc = create_word_doc(improved)
        file_path = "resume.docx"
        doc.save(file_path)

        with open(file_path, "rb") as f:
            st.download_button("📥 Download Word Resume", f, "resume.docx")
    else:
        st.warning("Upload resume first")

# ------------------------------
# CHATBOT
# ------------------------------
st.markdown("---")
st.subheader("💬 Career Chat")

user_input = st.text_input("Ask anything")

if st.button("Ask") and user_input:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}]
    )

    st.write(response.choices[0].message.content)

# ------------------------------
# 🎤 VOICE CHAT
# ------------------------------
st.markdown("---")
st.subheader("🎤 Voice Assistant")

if st.button("🎤 Record Voice"):
    audio_file = record_audio()

    with open(audio_file, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f
        )

    st.write("You said:", transcript.text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": transcript.text}]
    )

    st.write(response.choices[0].message.content)

# ------------------------------
# MOCK INTERVIEW
# ------------------------------
st.markdown("---")
st.subheader("🎯 Mock Interview")

if "history" not in st.session_state:
    st.session_state.history = []

if st.button("Start Interview"):
    st.session_state.history = []
    q = mock_interview("", resume_text)
    st.session_state.history.append(q)
    st.write(q)

answer = st.text_input("Your answer")

if st.button("Submit Answer") and answer:
    st.session_state.history.append(answer)

    next_q = mock_interview(st.session_state.history, resume_text)
    st.session_state.history.append(next_q)

    st.write(next_q)
