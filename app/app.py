import streamlit as st
import openai

# Set your API key
openai.api_key = "YOUR_OPENAI_API_KEY"

st.title("💬 AI Job Assistant")

user_input = st.text_area("Ask me anything about jobs, resumes, or skills:")

if st.button("Ask"):

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful career assistant helping students with job applications."},
            {"role": "user", "content": user_input}
        ]
    )

    answer = response["choices"][0]["message"]["content"]

    st.write(answer)
