import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# UI
st.title("AI Job Assistant")

user_input = st.text_input("Ask me anything about jobs, resumes, or skills:")

if st.button("Ask"):
    if user_input:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_input}
            ]
        )

        st.write(response.choices[0].message.content)
