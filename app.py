import streamlit as st
import os
import pandas as pd
import plotly.express as px
from openai import OpenAI
import re

# -------------------------
# OpenAI Client
# -------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="🔥 A2 Writing Dashboard", page_icon="📝", layout="wide")
st.title("🔥 A2 Semantic Writing Evaluator & Dashboard")
st.write("Enter student writing (any length) below and get AI evaluation with detailed feedback and class-level stats:")

# Text input
text = st.text_area("Student Writing", height=200)

# Initialize session state for storing results
if "results" not in st.session_state:
    st.session_state.results = []

# -------------------------
# AI Evaluation Function
# -------------------------
def ai_evaluate(text):
    word_count = len(text.strip().split())
    
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
- Detailed A2-friendly feedback (4–6 sentences, constructive, explain mistakes, give improvement tips)
- Word count of the student's text

Student Writing:
{text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_text = response.choices[0].message.content

        # Score extraction
        score_match = re.search(r"Score\s*out\s*of\s*20\s*:\s*(\d+)", ai_text)
        score = int(score_match.group(1)) if score_match else None

        # CEFR extraction
        grade_match = re.search(r"CEFR grade\s*[:\-]\s*([A-E])", ai_text, re.IGNORECASE)
        grade = grade_match.group(1).upper() if grade_match else None

        return {"feedback": ai_text, "word_count": word_count, "score": score, "grade": grade}

    except Exception as e:
        st.error(f"⚠️ AI evaluation failed: {e}")
        return {"feedback": None, "word_count": word_count, "score": None, "grade": None}

# -------------------------
# Evaluate Button
# -------------------------
if st.button("Evaluate with AI"):
    if text.strip():
        with st.spinner("AI is evaluating..."):
            result = ai_evaluate(text)

        # Word count warnings
        if result["word_count"] < 30:
            st.warning("⚠️ Your text is short (<30 words). AI evaluation still provided.")
        if result["word_count"] > 60:
            st.warning("⚠️ Expected word count exceeded (>60 words). AI evaluation still provided.")

        if result["feedback"]:
            st.subheader("📊 AI Evaluation Result")
            st.text(result["feedback"])
            st.success(f"Word count: {result['word_count']} | Score: {result['score']} | CEFR Grade: {result['grade']}")

            # Save to session state
            st.session_state.results.append({
                "text": text,
                "feedback": result["feedback"],
                "word_count": result["word_count"],
                "score": result["score"],
                "grade": result["grade"]
            })
    else:
        st.warning("Please write some text first!")

# -------------------------
# Global Dashboard
# -------------------------
if st.session_state.results:
    st.subheader("📈 Global Dashboard")
    df = pd.DataFrame(st.session_state.results)

    # Word count histogram
    fig_wc = px.histogram(df, x="word_count", nbins=10, title="Word Count Distribution")
    st.plotly_chart(fig_wc, use_container_width=True)

    # CEFR grade histogram with colors
    cefr_colors = {
        "A": "green",
        "B": "lime",
        "C": "orange",
        "D": "red",
        "E": "darkred",
        None: "gray"
    }
    df["color"] = df["grade"].apply(lambda g: cefr_colors.get(g, "gray"))

    fig_grade = px.histogram(df, x="grade", title="CEFR Grade Distribution", color="color",
                             color_discrete_map=cefr_colors)
    st.plotly_chart(fig_grade, use_container_width=True)

    # Average score
    avg_score = df["score"].dropna().mean()
    st.metric("⭐ Average Score", f"{avg_score:.2f}/20")

    # Feedback table
    st.dataframe(df[["text", "word_count", "score", "grade", "feedback"]])

    # Export CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name="student_writing_results.csv", mime="text/csv")
