import streamlit as st
import yt_dlp
import os
import json

st.set_page_config(page_title="AFL Replay Custom Download")
st.title("Single Replay Micro-Test with Custom Save Folder")

# Known replay info
video = {
    "id": "1362116",
    "slug": "match-replay-gold-coast-v-collingwood",
    "title": "Match Replay: Gold Coast v Collingwood",
    "duration": "2h11m",
    "thumbnail": "https://images.afl.com.au/image/private/t_editorial_landscape_1024/f_auto/1362116/yrmdu1xazgslexqwcfqi.jpg",
    "url": "https://www.afl.com.au/video/1362116/match-replay-gold-coast-v-collingwood"
}

# --- Custom folder input ---
st.markdown("### 📁 Choose Save Folder")
save_path = st.text_input(
    "Enter your full save path (e.g. /Users/anthony/OneDrive/AFL_Replays)",
    value="./AFL_Replays"
)
st.text(f"Save location: {save_path}")

# --- Make folder if needed ---
if not os.path.exists(save_path):
    try:
        os.makedirs(save_path)
    except Exception as e:
        st.warning(f"⚠️ Could not create folder: {e}")

# --- Preview Replay ---
st.image(video["thumbnail"], caption=f"{video['title']} ({video['duration']})")
st.write(f"📄 **Title**: {video['title']}")
st.write(f"🔗 [Replay Link]({video['url']})")

# --- Dry Run Metadata Preview ---
st.markdown("### ▶️ Pre-Download Metadata Check")
try:
    with yt_dlp.YoutubeDL({"quiet": False}) as ydl:
        info = ydl.extract_info(video["url"], download=False)
    st.success("Metadata extracted!")

    if "formats" in info and info["formats"]:
        st.info(f"Found {len(info['formats'])} formats.")
        for fmt in info["formats"][:5]:
            st.write(f"- {fmt.get('format_id')}: {fmt.get('ext')} @ {fmt.get('height')}p")
    else:
        st.warning("No formats found.")

    st.text(f"Extractor: {info.get('_type')} | Title: {info.get('title')}")
except Exception as e:
    st.error("❌ Metadata extraction failed.")
    st.text(str(e))

# --- Download Button ---
if st.button("⬇️ Download This Replay"):
    ydl_opts = {
        "outtmpl": os.path.join(save_path, f"{video['title']}.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            st.info("Downloading… please wait.")
            ydl.download([video["url"]])
        st.success("✅ Download complete!")
    except Exception as e:
        st.error("❌ Download failed.")
        st.text(str(e))

# --- List Downloaded Files ---
st.markdown("---")
st.subheader("Downloaded Replays")

if os.path.isdir(save_path):
    files = sorted(os.listdir(save_path))
    st.text(f"📁 Folder contains: {files}")

    if not files:
        st.info("No files downloaded yet.")
    else:
        for fname in files:
            fpath = os.path.join(save_path, fname)
            if os.path.isfile(fpath):
                with open(fpath, "rb") as fp:
                    st.download_button(
                        label=f"⬇️ {fname}",
                        data=fp.read(),
                        file_name=fname,
                        mime="video/mp4"
                    )
else:
    st.warning("The folder does not exist.")
