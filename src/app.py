import streamlit as st
st.set_page_config(initial_sidebar_state="expanded")
import retriever  # our "brain" — the file with the retrieve() function
from voice import generate_speech

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

# --- Set up audio cache: maps message index → audio bytes for played voice answers ---
if "audio_cache" not in st.session_state:
    st.session_state.audio_cache = {}

# --- Helper: render one assistant message with its audio button ---
# Defined once, called from the replay loop below.
def render_assistant_message(message_text: str, caption_text: str, message_index: int):
    """Render an assistant answer with its tier badge and 🔊 Listen button/player."""
    st.write(message_text)
    st.caption(caption_text)

    # If audio for this message has been generated before, show the player
    if message_index in st.session_state.audio_cache:
        st.audio(st.session_state.audio_cache[message_index], format="audio/mp3")
    else:
        # Otherwise, show a button to generate it on demand
        if st.button("🔊 Listen", key=f"listen_{message_index}"):
            with st.spinner("Generating audio..."):
                audio_bytes = generate_speech(message_text)
            if audio_bytes is None:
                st.warning("Audio unavailable. Please try again.")
            else:
                st.session_state.audio_cache[message_index] = audio_bytes
                st.rerun()


# --- Replay the whole conversation so far on every re-run ---
# This is what makes buttons on old messages keep working.
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            render_assistant_message(message["content"], message.get("caption", ""), idx)
        else:
            st.write(message["content"])


# --- Handle a new question (only when the user submits one) ---
if question := st.chat_input("Ask about London Tech Week..."):

    # 1. Save the user's question to memory and show it
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # 2. Hand the question to the brain and get the answer
    result = brain.retrieve(question)

    # 3. Build the tier badge text
    if result["tier"] == 1:
        caption = f"🎯 Direct hit (Tier 1) · source: {result['source']} · distance {result['distance']:.3f}"
    elif result["tier"] == 2:
        caption = f"🤖 Claude synthesis (Tier 2) · closest source: {result['source']} · distance {result['distance']:.3f}"
    else:
        caption = f"🌐 Web search (Tier 3) · {result['source']}"

    # 4. Save the answer to memory and render it (including audio button)
    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "caption": caption}
    )
    message_index = len(st.session_state.messages) - 1
    with st.chat_message("assistant"):
        render_assistant_message(result["answer"], caption, message_index)
        