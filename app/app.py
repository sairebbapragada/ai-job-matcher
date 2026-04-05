import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
import pandas as pd

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page setup
st.set_page_config(page_title="AI Career Assistant", layout="wide")

st.title("🚀 AI Career Assistant")

# ---------------------------
# 📄 Resume Upload
# ---------------------------
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

resume_text = ""
if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
    st.success("Resume uploaded!")

# ---------------------------
# 💼 Job Description
# ---------------------------
job_desc = st.text_area("Paste Job Description")

# ---------------------------
# 🎯 JOB MATCHING
# ---------------------------
def get_match_analysis(resume, job):
    prompt = f"""
    Compare this resume with the job description.

    Return:
    - Match score (0-100)
    - Strengths
    - Missing skills
    - Suggestions

    Resume:
    {resume}

    Job:
    {job}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

if st.button("Match Resume to Job"):
    if resume_text and job_desc:
        result = get_match_analysis(resume_text, job_desc)

        st.subheader("🎯 Match Analysis")
        st.write(result)

        # simple visualization
        st.subheader("📊 Sample Match Visualization")
        df = pd.DataFrame({
            "Category": ["Match", "Gap"],
            "Value": [70, 30]
        })
        st.bar_chart(df.set_index("Category"))
    else:
        st.warning("Upload resume and paste job description")

# ---------------------------
# 💬 CHATBOT
# ---------------------------
st.subheader("💬 Career Chatbot")

user_input = st.text_input("Ask anything about jobs, resumes, or skills")

if st.button("Ask AI"):
    if user_input:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful career assistant."},
                {"role": "user", "content": user_input}
            ]
        )

        st.write(response.choices[0].message.content)
