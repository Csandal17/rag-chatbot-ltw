"""
Voice module for the LTW chatbot.

Wraps the ElevenLabs Text-to-Speech API into a simple generate_speech() function
that app.py can call when a user clicks the 🔊 button on an answer.
"""

import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables from .env file (ANTHROPIC_API_KEY, TAVILY_API_KEY, ELEVENLABS_API_KEY)
load_dotenv()

# Create the ElevenLabs client once, when this module is first imported.
# This is more efficient than creating a new client for every TTS call.
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Voice ID for our LTW Assistant.
# "Emilia Bennett" — young, British, conversational. Chosen for warmth and calm,
# matching the LTW Assistant's role as an approachable event guide.
LTW_VOICE_ID = "E4IXevHtHpKGh0bvrPPr"

def generate_speech(text: str) -> bytes:
    """
    Convert text to speech using ElevenLabs and return the audio as bytes.

    Args:
        text: The text to be spoken. Typically a chatbot answer.

    Returns:
        Audio bytes in MP3 format, ready to be played by Streamlit's st.audio().
    """
    try:
        # Call the ElevenLabs Text-to-Speech endpoint.
        # This returns a generator of audio chunks (streaming), not one big blob.
        audio_stream = client.text_to_speech.convert(
            voice_id=LTW_VOICE_ID,
            text=text,
            model_id="eleven_multilingual_v2",
        )

        # Collect all the streamed chunks into a single bytes object.
        # b"" is an empty bytes object — like "" for strings, but for binary data.
        audio_bytes = b"".join(audio_stream)

        return audio_bytes

    except Exception as e:
        # If anything goes wrong (network error, API error, etc.), log it and return None.
        # app.py will check for None and show an error to the user instead of crashing.
        print(f"❌ ElevenLabs error: {e}")
        return None
    
# --- Standalone test: run this file directly to generate a test.mp3 ---
# Only runs when you execute `python src/voice.py` directly.
# Does NOT run when app.py imports generate_speech() from this file.
if __name__ == "__main__":
    test_text = "Hello London. The London Tech Week assistant is ready."
    print(f"Generating speech for: {test_text!r}")

    audio = generate_speech(test_text)

    if audio is None:
        print("❌ Speech generation failed — check the error above.")
    else:
        output_path = "test_voice_module.mp3"
        with open(output_path, "wb") as f:
            f.write(audio)
        print(f"✅ Success! {len(audio):,} bytes saved to {output_path}")
        print(f"   Open Finder and double-click {output_path} to play it.")

# --- Standalone test: run this file directly to generate a test.mp3 ---
# Only runs when you execute `python src/voice.py` directly.
# Does NOT run when app.py imports generate_speech() from this file.
if __name__ == "__main__":
    test_text = "Hello London. The London Tech Week assistant is ready."
    print(f"Generating speech for: {test_text!r}")

    audio = generate_speech(test_text)

    if audio is None:
        print("❌ Speech generation failed — check the error above.")
    else:
        output_path = "test_voice_module.mp3"
        with open(output_path, "wb") as f:
            f.write(audio)
        print(f"✅ Success! {len(audio):,} bytes saved to {output_path}")
        print(f"   Open Finder and double-click {output_path} to play it.")

    