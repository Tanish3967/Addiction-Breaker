import streamlit as st
from datetime import datetime
import random
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Recovery AI Agent
recovery_agent = Agent(
    name="Addiction Recovery Agent",
    description="Helps users with addiction recovery strategies and motivation.",
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    instructions=[
        "You are a kind and supportive recovery counselor AI.",
        "Provide helpful, compassionate advice for breaking addiction habits.",
        "Use simple and encouraging language.",
        "If unsure, suggest talking to a real therapist or support group."
    ],
    show_tool_calls=True,
    markdown=True
)

# Initialize session state
if 'streak' not in st.session_state:
    st.session_state.streak = 0
    st.session_state.last_check = None
    st.session_state.history = []
    st.session_state.estimated_days = None
    st.session_state.assessment_done = False

# Addiction Type
st.title("🧠 Addiction Breaker AI + Groq Chatbot")
addiction_type = st.selectbox("Choose your addiction type:", [
    "Smoking", "Alcohol", "Phone/Social Media", "Sugar/Junk Food", "Gaming", "Other"
])

# Assessment
st.header("🧪 Recovery Assessment")
if not st.session_state.assessment_done:
    q1 = st.slider("How long have you had this addiction? (in years)", 0, 20, 2)
    q2 = st.slider("How many times a day do you indulge?", 0, 50, 5)
    q3 = st.slider("How motivated are you to quit? (10 = highly motivated)", 1, 10, 7)
    q4 = st.slider("How supportive is your environment? (10 = very supportive)", 1, 10, 6)

    if st.button("🔍 Assess My Recovery Journey"):
        base_days = 21
        severity_factor = (q1 * 2 + q2) / 2
        motivation_factor = (11 - q3)
        environment_factor = (11 - q4)
        estimate = int(base_days + severity_factor + motivation_factor * 2 + environment_factor * 2)
        st.session_state.estimated_days = max(estimate, 21)
        st.session_state.assessment_done = True
        st.success("Assessment completed!")

if st.session_state.assessment_done:
    st.subheader(f"🗓 Estimated Recovery Time: **{st.session_state.estimated_days} days**")

# Daily Check-in
st.header("📅 Daily Check-in")
today = datetime.now().date()
if st.session_state.last_check != today:
    choice = st.radio("Did you give in to your addiction today?", ("No 💪", "Yes 😞"))
    if st.button("Submit Response"):
        st.session_state.last_check = today
        if choice == "No 💪":
            st.session_state.streak += 1
        else:
            st.session_state.streak = 0
        st.session_state.history.append((str(today), choice))
        st.success("Thanks for checking in today!")
else:
    st.info("✅ Already checked in today.")

# Streak
st.header("🔥 Current Streak")
st.metric("Days without giving in", st.session_state.streak)

# Motivation
motivational_quotes = [
    "One day at a time. You’re doing great!",
    "Cravings are temporary. Your goal is forever.",
    "The struggle you’re in today is developing the strength you need tomorrow.",
    "Every moment is a fresh beginning.",
    "Proud of you for showing up today!"
]
st.header("💬 Motivation")
st.info(random.choice(motivational_quotes))

# History
st.header("📜 Check-in History")
for date, status in reversed(st.session_state.history):
    st.write(f"**{date}** - {status}")

# Chatbot
st.header("💡 Ask the Addiction Recovery Bot (Groq-Powered)")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask something like 'How do I handle cravings?' or 'What to do if I relapse?'", key="chat")

if st.button("Ask AI"):
    if user_input:
        response = recovery_agent.invoke(f"My addiction is {addiction_type}. Question: {user_input}")
        st.session_state.chat_history.append((user_input, response))
        st.text_area("💬 Response", response, height=150)

# Display chat history
if st.session_state.chat_history:
    st.subheader("🗨 Chat History")
    for i, (q, r) in enumerate(reversed(st.session_state.chat_history[-5:])):
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {r}")
        st.markdown("---")
