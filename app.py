import streamlit as st
from utils import generate_roadmap

st.set_page_config(page_title="AI Roadmap Builder", layout="centered")

st.title("🧠 AI-Powered Roadmap Builder")
goal = st.text_input("Enter your goal (e.g., Learn Python, Start a business)")

if st.button("Generate Roadmap") and goal:
    with st.spinner("Generating your 5-step plan..."):
        roadmap = generate_roadmap(goal)
        st.success("Here's your plan:")
        st.markdown(roadmap)
st.subheader("🔧 Refine a Step")
step_to_refine = st.text_input("Paste a step you want to improve:")
user_feedback = st.text_input("How would you like it improved?")

if st.button("Refine Step"):
    refine_prompt = f"Rewrite this step with the following instruction:\nStep: {step_to_refine}\nInstruction: {user_feedback}"
    refined = generate_roadmap(refine_prompt)
    st.markdown("**Refined Step:**")
    st.markdown(refined)
import os

templates = os.listdir("roadmap_templates")
choice = st.selectbox("📁 Load a template", templates)
if st.button("Load Template"):
    with open(f"roadmap_templates/{choice}", "r") as file:
        st.markdown(file.read())
from fpdf import FPDF

def export_as_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)
    pdf.output("my_roadmap.pdf")

if st.button("📄 Download as PDF"):
    export_as_pdf(roadmap)
    st.success("Saved as my_roadmap.pdf")
st.subheader("📈 Track Your Progress")
steps = roadmap.split("\n")
completed = st.session_state.get("completed", [False] * len(steps))

for i, step in enumerate(steps):
    completed[i] = st.checkbox(step, value=completed[i])
st.session_state["completed"] = completed
st.subheader("✏️ Customize Steps")
new_step = st.text_input("Add a new step:")
if st.button("➕ Add Step"):
    steps.append(f"Step {len(steps)+1}: {new_step}")
language = st.selectbox("🌐 Choose Language", ["English", "Tamil", "Hindi", "French"])
if st.button("Translate"):
    lang_prompt = f"Translate this roadmap to {language}: {roadmap}"
    translated = generate_roadmap(lang_prompt)
    st.markdown(translated)
