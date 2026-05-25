import streamlit as st

import retriever  # our "brain" — the file with the retrieve() function


# --- Open Chroma ONCE and remember it, instead of every time the page re-runs ---
@st.cache_resource
def load_brain():
    return retriever  # importing already ran the setup; just hand it back


brain = load_brain()


st.title("London Tech Week 2026 Assistant")
st.caption("Ask about sessions, speakers, and the schedule.")


# --- A box for the user to type their question ---
question = st.text_input("Your question:")


# --- When there's a question, hand it to the brain and show the answer ---
if question:
    result = brain.retrieve(question)        # hand the question over, catch the tray

    st.write(result["answer"])               # show the answer text

    # Show a small badge saying which tier answered
    if result["tier"] == 1:
        st.caption(f"🎯 Direct hit (Tier 1) · distance {result['distance']:.3f}")
    else:
        st.caption(f"🤖 Claude synthesis (Tier 2) · distance {result['distance']:.3f}")

    