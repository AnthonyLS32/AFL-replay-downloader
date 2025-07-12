import streamlit as st
import yt_dlp
import requests
import io
import os

st.set_page_config(page_title="AFL Replay Micro-Test")
st.title("Single Replay Micro-Test")

# Static known video
video = {
    "id": "1362116",
    "slug": "match-replay-gold-coast-v-collingwood",
    "title": "Match Replay: Gold Coast v Collingwood",
    "duration": "2h11m",
    "thumbnail": "https://images.afl.com.au/image/private/t_editorial_landscape_1024/f_auto/1362116/yrmdu1xazgslexqwcfqi.jpg",
    "url": "https://www.afl.com.au/video/1362116/match-replay-gold-coast-v-collingwood"
}

DL_DIR = "./AFL_Replays"
os.makedirs(DL_DIR, exist_ok=True)

st.image(video["thumbnail"], caption=f"{video['title']} ({video['duration']})")
st.write(f"📄 **Title**: {video['title']}")
st.write(f"🔗 [Replay Link]({video['url']})")

if st.button("Download This Replay"):
    st.info("Downloading via yt-dlp…")

    ydl_opts = {
        "outtmpl": os.path.join(DL_DIR, f"{video['title']}.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video["url"]])
            st.success("✅ Download complete!")
        except Exception as e:
            st.error(f"❌ Download failed: {e}")
