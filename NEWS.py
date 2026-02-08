import streamlit as st
import requests
from groq import Groq
from elevenlabs.client import ElevenLabs
from datetime import datetime

# --- 1. CONFIGURATION (Using Streamlit Secrets) ---
# We use st.secrets so your keys stay private and safe!
try:
    GROQ_API_KEY = st.secrets["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"]
    ELEVENLABS_API_KEY = st.secrets["c326593c9a8d19effe408569f7dbd94e3287833ac6373963eec51fb01501d3c6"]
    NEWS_API_KEY = st.secrets["4a97024c45b14ba397b8aff8e63ab439"]
except:
    st.error("Missing API Keys! Go to Settings > Secrets and add them.")
    st.stop()

st.set_page_config(page_title="AI Radio One", layout="wide", page_icon="📻")

def get_live_news(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&language=en&apiKey={NEWS_API_KEY}"
    return requests.get(url).json().get("articles", [])[:3]

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("📻 Station Control")
    target_lang = st.selectbox("Broadcast Language", ["English", "Spanish", "French", "German", "Hindi"])
    news_cat = st.selectbox("News Category", ["technology", "business", "science", "sports", "health"])

# --- 3. MAIN INTERFACE ---
st.title("📡 AI Radio One: Live Global Broadcast")

if st.button("🔴 START LIVE BROADCAST"):
    try:
        articles = get_live_news(news_cat)
        if not articles:
            st.warning("No news found. Check your NewsAPI key.")
        else:
            headlines = []
            cols = st.columns(len(articles))
            for i, art in enumerate(articles):
                with cols[i]:
                    if art.get("urlToImage"): st.image(art["urlToImage"], use_container_width=True)
                    st.subheader(art.get("title")[:60] + "...")
                    headlines.append(art.get("title"))

            with st.status("🎙️ AI DJ is preparing the script..."):
                client_groq = Groq(api_key=GROQ_API_KEY)
                prompt = f"Summarize into a 30-sec high-energy radio script in {target_lang}: {' . '.join(headlines)}. Output ONLY the spoken words."
                completion = client_groq.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant"
                )
                script = completion.choices[0].message.content
                st.write(f"**DJ Script:** {script}")

                client_el = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                audio_iterator = client_el.text_to_speech.convert(
                    text=script, voice_id="JBFqnCBsd6RMkjVDRZzb",
                    model_id="eleven_multilingual_v2"
                )
                audio_bytes = b"".join(list(audio_iterator))
                st.audio(audio_bytes, format="audio/mp3")
    except Exception as e:
        st.error(f"Error: {e}")
