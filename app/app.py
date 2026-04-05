import streamlit as st
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AI Job Assistant")

user_input = st.text_input("Ask me about jobs:")

if user_input:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    
    st.write(response.choices[0].message.content)
