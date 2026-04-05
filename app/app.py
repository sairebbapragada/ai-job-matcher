import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
import re

# ---------------------------
# 🔑 Load API Key
# ---------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------
# 📄 PDF Reader
# ---------------------------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ---------------------------
# 🧠 Extract score from AI text
# ---------------------------
def extract_score(text):
    match = re.search(r"\b(\d{1,3})\b", text)
    if match:
        score = int(match.group(1))
        return min(score, 100)
    return 50

# ---------------------------
# 🎨 UI Setup
# ---------------------------
st.set_page_config(page_title="AI Career Assistant", layout="wide")

st.title("🚀 AI Career Assistant")
st.markdown("### Get resume feedback, job matching, and career guidance")

# ---------------------------
# 📄 + 💼 Layout
# ---------------------------
col1, col2 = st.columns(2)

# LEFT: Resume
with col1:
    st.subheader("📄 Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    resume_text = ""
    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)
        st.success("Resume uploaded successfully!")

# RIGHT: Job Description
with col2:
    st.subheader("💼 Job Description")
    job_desc = st.text_area("Paste job description here")

# ---------------------------
# 🎯 MATCH BUTTON
# ---------------------------
if st.button("🚀 Match Me"):
    if uploaded_file and job_desc:

        with st.spinner("Analyzing..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"""
                    Compare this resume and job description.

                    Return:
                    1. Match score (0-100)
                    2. Strengths
                    3. Missing skills
                    4. Suggestions

                    Resume:
                    {resume_text}

                    Job:
                    {job_desc}
                    """
                }]
            )

            result = response.choices[0].message.content

        # Extract score
        score = extract_score(result)

        # Display results
        st.subheader("🎯 Match Results")
        st.write(result)

        st.subheader(f"📊 Match Score: {score}%")
        st.progress(score / 100)

    else:
        st.warning("Please upload resume and paste job description")

# ---------------------------
# 💬 CHATBOT
# ---------------------------
st.subheader("💬 Career Assistant")

user_input = st.text_input("Ask anything about jobs, resumes, or skills")

if st.button("Ask AI"):
    if user_input:

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful career assistant."},
                    {"role": "user", "content": user_input}
                ]
            )

            st.write(response.choices[0].message.content)job_desc = st.text_area("Paste Job Description")

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
