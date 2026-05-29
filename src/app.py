import streamlit as st
st.set_page_config(initial_sidebar_state="expanded")
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
        "- **172** Q/A pairs indexed in a vector database\n"
        "- 🎯 **Tier 1:** Direct hit\n"
        "- 🤖 **Tier 2:** AI synthesis\n"
        "- 🌐 **Tier 3:** Web search"
    )

    st.divider()

    st.markdown("**🎟️ The event**")
    st.markdown(
        "📅 **8–12 June 2026**\n\n"
        "📍 Olympia London\n\n"
        "🔗 [londontechweek.com](https://londontechweek.com)"
    )

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

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

# --- Set up the conversation memory (only runs once, on first load) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

    # --- Re-draw the whole conversation so far ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("caption"):
            st.caption(message["caption"])

# --- The chat input box (sits at the bottom of the page) ---
if question := st.chat_input("Ask about London Tech Week..."):

    # 1. Show the user's question immediately, and save it to memory
    with st.chat_message("user"):
        st.write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # 2. Hand the question to the brain and get the answer
    result = brain.retrieve(question)

    # 3. Build the tier badge text
    if result["tier"] == 1:
        caption = f"🎯 Direct hit (Tier 1) · source: {result['source']} · distance {result['distance']:.3f}"
    elif result["tier"] == 2:
        caption = f"🤖 Claude synthesis (Tier 2) · closest source: {result['source']} · distance {result['distance']:.3f}"
    else:
        caption = f"🌐 Web search (Tier 3) · {result['source']}"

    # 4. Show the answer, and save it to memory (with its badge)
    with st.chat_message("assistant"):
        st.write(result["answer"])
        st.caption(caption)
    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "caption": caption}
    )

