import streamlit as st
import pandas as pd

st.title("🚀 AI Job Matcher")

# Input
resume = st.text_area("Paste your resume here")

# Sample jobs (temporary)
jobs = [
    {"role": "Data Analyst", "company": "Target", "skills": "sql python power bi"},
    {"role": "Data Scientist", "company": "Amazon", "skills": "python machine learning aws"},
    {"role": "BI Analyst", "company": "Optum", "skills": "sql dashboards reporting"},
]

def match_score(resume, job_skills):
    resume_words = set(resume.lower().split())
    job_words = set(job_skills.split())
    
    if len(job_words) == 0:
        return 0
    
    return round(len(resume_words & job_words) / len(job_words) * 100, 2)

if st.button("Find Matches"):
    results = []

    for job in jobs:
        score = match_score(resume, job["skills"])
        results.append({
            "Role": job["role"],
            "Company": job["company"],
            "Match %": score
        })

    df = pd.DataFrame(results).sort_values(by="Match %", ascending=False)

    st.subheader("Top Matches")
    st.dataframe(df)
    st.bar_chart(df.set_index("Role")["Match %"])
