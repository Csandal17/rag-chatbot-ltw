import streamlit as st

import retriever  # our "brain" — the file with the retrieve() function


# --- Open Chroma ONCE and remember it, instead of every time the page re-runs ---
@st.cache_resource
def load_brain():
    return retriever  # importing already ran the setup; just hand it back


brain = load_brain()

# --- Sidebar: about, stats, and event details ---
with st.sidebar:
    st.title("🤖 About")
    st.markdown(
        "An AI assistant for **London Tech Week 2026**. "
        "Ask about sessions, speakers, and the schedule, and it "
        "answers using a retrieval system built on the event's content."
    )

    st.divider()

    st.markdown("**⚙️ How it works**")
    st.markdown(
        "- **150** Q/A pairs indexed in a vector database\n"
        "- **Tier 1:** instant answer on a confident match\n"
        "- **Tier 2:** Claude synthesises an answer when needed"
    )

    st.divider()

    st.markdown("**🎟️ The event**")
    st.markdown(
        "📅 **8–12 June 2026**\n\n"
        "📍 Olympia London\n\n"
        "🔗 [londontechweek.com](https://londontechweek.com)"
    )
    
# --- Custom blue LTW header banner ---
st.markdown(
    """
    <div style="
        background-color: #2E2EFF;
        padding: 28px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
    ">
        <h1 style="color: #FFFFFF; margin: 0; font-size: 2.4rem;">
            London Tech Week 2026 Assistant
        </h1>
        <p style="color: #FFFFFF; margin: 6px 0 0 0; font-size: 1rem; opacity: 0.9;">
            📅 8–12 June 2026 &nbsp;·&nbsp; 📍 Olympia London
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

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

