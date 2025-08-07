import streamlit as st
import json
import random

# Load the questions once
if "questions" not in st.session_state:
    with open("questions.json", "r") as f:
        questions = json.load(f)
        random.shuffle(questions)
        st.session_state.questions = questions

# Initialize session state
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "submitted" not in st.session_state:
    st.session_state.submitted = False

questions = st.session_state.questions
q = questions[st.session_state.current_q]

st.title("🧠 SDN Quiz Bot with Citations")
st.markdown(f"**Q{st.session_state.current_q + 1}:** {q['question']}")

# Get user input
if q["type"] == "MCQ":
    user_ans = st.radio("Choose your answer:", q["options"], key=f"ans_{st.session_state.current_q}")
else:
    user_ans = st.text_input("Type your answer:", key=f"ans_{st.session_state.current_q}")

# Only show Submit if not submitted
if not st.session_state.submitted:
    if st.button("Submit", key=f"submit_{st.session_state.current_q}"):
        correct = q["answer"].strip().lower()
        user_input = user_ans.strip().lower()

        if user_input == correct:
            st.success("✅ Correct!")
            st.session_state.score += 1
        else:
            st.error("❌ Incorrect.")

        st.markdown(f"📖 **Citation:** {q['citation']}")
        st.session_state.submitted = True
else:
    # Only show Next after submission
    if st.button("Next", key=f"next_{st.session_state.current_q}"):
        if st.session_state.current_q + 1 < len(questions):
            st.session_state.current_q += 1
            st.session_state.submitted = False
        else:
            st.success(f"🎉 Quiz completed! Your score: {st.session_state.score}/{len(questions)}")
            st.stop()