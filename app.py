# app.py
# -------------------------
# A2 Semantic Writing Evaluator (Streamlit + OpenAI)
# -------------------------

import streamlit as st
import os
from openai import OpenAI

# -------------------------
# Load API Key from .env
# -------------------------
# .env dosyasının içinde:
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
load_dotenv(override=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="🔥 AI Semantic Writing Evaluator", page_icon="📝")
st.title("🔥 AI Semantic Writing Evaluator")
st.write("Evaluate A2-level student writing using AI. Enter the text below:")

# Text area for student writing
text = st.text_area("Student Writing", height=200)

# -------------------------
# AI Evaluation Function
# -------------------------
def ai_evaluate(text):
    """
    Sends the student's text to OpenAI and returns evaluation results:
    - Score out of 20
    - CEFR grade (A–E)
    - Short A2-friendly feedback
    - Word count
    """
    
    prompt = f"""
You are an experienced English teacher evaluating an A2-level student's writing.

Evaluate using these criteria:
- Task achievement
- Vocabulary quality
- Grammar accuracy
- Coherence and organization
- Communication effectiveness

Give:
- Score out of 20
- CEFR grade (A–E)
- Short A2-friendly feedback (2–3 sentences)
- Word count of the student's text

Student Writing:
{text}
"""

    # Send prompt to OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # veya gpt-4.1-mini
        messages=[{"role": "user", "content": prompt}]
    )

    # Return AI response text
    return response.choices[0].message.content

# -------------------------
# Streamlit Button & Output
# -------------------------
if st.button("Evaluate with AI"):

    if text.strip():
        with st.spinner("AI is evaluating..."):
            result = ai_evaluate(text)

        st.subheader("📊 AI Evaluation Result")
        st.text(result)  # Daha temiz görünüm için text kullanıyoruz
    else:
        st.warning("Please write some text first!")
