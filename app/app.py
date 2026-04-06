import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
import re

# ------------------------------
# CONFIG
# ------------------------------
st.set_page_config(page_title="FastTrack AI", layout="wide")
# ------------------------------
# API KEY (FINAL FIX)
# ------------------------------
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.error("API key missing")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------------------------
# UI STYLE
# ------------------------------
st.markdown("""
<style>
.main { background-color: #0e1117; }
h1, h2, h3 { color: white; }
p, div, label { color: #d1d5db; font-size: 16px; }
.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 10px 16px;
}
textarea { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# FUNCTIONS
# ------------------------------
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_score(text):
    match = re.search(r"\b(\d{1,3})\b", text)
    return min(int(match.group(1)), 100) if match else 50

# ------------------------------
# HEADER
# ------------------------------
# ------------------------------
# HEADER
# ------------------------------
st.title("🚀 FastTrack AI")
st.write("Fast-track your career with AI-powered resume optimization, job matching, and interview prep")

st.divider()st.title("🚀 FastTrack AI")
st.write("Your AI career assistant — optimize resumes, explore roles, and prepare for interviews")

st.divider()

# ------------------------------
# INPUT
# ------------------------------
st.subheader("📄 Upload Resume")
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

resume = ""
if uploaded_file:
    st.success("✅ Resume uploaded successfully")
    resume = extract_text(uploaded_file)

st.subheader("💼 Job Description")
job_desc = st.text_area("Paste job description")

col1, col2, col3 = st.columns(3)

with col1:
    analyze = st.button("Analyze Match")

with col2:
    suggest_jobs = st.button("Suggest Jobs")

with col3:
    generate_questions = st.button("Interview Prep")

st.divider()

# ------------------------------
# ANALYSIS
# ------------------------------
if uploaded_file and job_desc and analyze:

    st.subheader("🎯 Match Analysis")

    with st.spinner("Analyzing..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
Analyze this resume vs job description.

Return:
1. Match score (0-100)
2. Missing skills
3. Resume improvements (bullet points)
4. Suggestions to improve experience

Resume:
{resume}

Job:
{job_desc}
"""
            }]
        )

        output = response.choices[0].message.content
        st.write(output)

        score = extract_score(output)
        st.progress(score / 100)
        st.write(f"Match Score: {score}%")

# ------------------------------
# JOB SUGGESTIONS
# ------------------------------
if uploaded_file and suggest_jobs:

    st.subheader("💼 Recommended Roles")

    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly career coach."},
                {"role": "user", "content": f"""
Based on this resume, suggest 5 job roles.

Include:
- Job title
- Why it's a good fit
- Key skills needed

Resume:
{resume}
"""}
            ]
        )

        st.write(response.choices[0].message.content)

# ------------------------------
# INTERVIEW CARDS (SWIPE STYLE)
# ------------------------------
if "questions" not in st.session_state:
    st.session_state.questions = []
    st.session_state.q_index = 0

if uploaded_file and generate_questions:

    with st.spinner("Generating questions..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
Generate 5 strong interview questions.

Resume:
{resume}
"""
            }]
        )

        questions = response.choices[0].message.content.split("\n")
        st.session_state.questions = [q for q in questions if q.strip()]
        st.session_state.q_index = 0

if st.session_state.questions:

    st.subheader("🔥 Interview Practice")

    q = st.session_state.questions[st.session_state.q_index]

    st.markdown(f"""
    <div style="
        background-color:#1f2937;
        padding:30px;
        border-radius:12px;
        text-align:center;
        font-size:22px;
        margin-bottom:20px;
    ">
    💡 {q}
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col1:
        if st.button("❌ Skip"):
            st.session_state.q_index += 1

    with col2:
        if st.button("💬 Get Tip"):
            tip = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"Give a strong answer tip for:\n{q}"
                }]
            )
            st.info(tip.choices[0].message.content)

    with col3:
        if st.button("✅ Got It"):
            st.session_state.q_index += 1

    if st.session_state.q_index >= len(st.session_state.questions):
        st.session_state.q_index = 0

# ------------------------------
# CHATBOT
# ------------------------------
st.divider()
st.subheader("💬 Career Chat")

user_input = st.text_input("Ask me anything about your career 👇")

if st.button("Ask AI"):
    if user_input:
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are a friendly career coach.

Talk like a helpful friend:
- Be casual and encouraging
- Give simple advice
- Avoid robotic tone
"""
                    },
                    {"role": "user", "content": user_input}
                ]
            )

            st.write(response.choices[0].message.content)
