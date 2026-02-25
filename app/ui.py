import sys
import os
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from app.pipeline import run_pipeline

st.set_page_config(page_title="Auto Video Publisher", layout="wide")
st.title("🚀 Auto Video Publisher")

# ---------------------------
# AUTO LOAD YOUTUBE CREDENTIAL
# ---------------------------
YOUTUBE_CREDENTIAL_PATH = os.path.join(ROOT_DIR, "credentials", "youtube.json")

if not os.path.exists(YOUTUBE_CREDENTIAL_PATH):
    st.error("❌ credentials/youtube.json not found")
    st.stop()

# ---------------------------
# SELECT POSTS DIRECTORY
# ---------------------------
default_posts_path = os.path.join(ROOT_DIR, "posts")

posts_root = st.text_input(
    "Posts Directory Path",
    value=default_posts_path
)

if not os.path.exists(posts_root):
    st.error("Invalid posts directory path")
    st.stop()

# ---------------------------
# DETECT POST FOLDERS
# ---------------------------
all_post_folders = [
    str(p)
    for p in Path(posts_root).iterdir()
    if p.is_dir()
]

selected_folders = st.multiselect(
    "Select Post Folders to Process",
    all_post_folders
)

# ---------------------------
# PLATFORM SELECTION
# ---------------------------
platforms = st.multiselect(
    "Select Platforms",
    ["YouTube", "Instagram", "Twitter"],
    default=["YouTube"]
)

skip_validation = st.checkbox("Skip Human Validation (Auto Upload)")

# ---------------------------
# SESSION STATE
# ---------------------------
if "start_batch" not in st.session_state:
    st.session_state.start_batch = False

if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

# ---------------------------
# PREVIEW MODE
# ---------------------------
if selected_folders and not skip_validation and not st.session_state.confirmed:

    st.subheader("📋 Preview Selected Posts")

    for folder in selected_folders:
        st.write(folder)

    if st.button("Confirm & Start Publishing"):
        st.session_state.confirmed = True
        st.session_state.start_batch = True

# ---------------------------
# DIRECT START
# ---------------------------
if skip_validation:
    if st.button("Start Batch Publishing"):
        st.session_state.start_batch = True

# ---------------------------
# PIPELINE EXECUTION
# ---------------------------
if st.session_state.start_batch and selected_folders:

    for folder in selected_folders:

        st.subheader(f"Processing: {folder}")

        pipeline_steps = [
            "Loading Post",
            "Validating Metadata",
            "Compressing Thumbnail",
            "Authenticating YouTube",
            "Uploading Video",
            "Uploading Thumbnail",
            "Logging to Excel",
        ]

        step_states = {step: "pending" for step in pipeline_steps}

        # Create a placeholder container ONCE
        steps_container = st.empty()

        def render_steps():
            with steps_container.container():
                for step in pipeline_steps:
                    status = step_states[step]

                    if isinstance(status, int):
                        st.info(f"⏳ {step} — {status}%")
                        st.progress(status / 100)
                    elif status == "done":
                        st.success(f"✔ {step}")
                    elif status == "running":
                        st.info(f"⏳ {step}")
                    else:
                        st.write(f"⬜ {step}")

        def step_callback(step, status):
            step_states[step] = status
            render_steps()

        try:
            render_steps()  # initial render

            url = run_pipeline(
                folder,
                YOUTUBE_CREDENTIAL_PATH,
                platforms,
                skip_validation,
                step_callback
            )

            st.success(f"🎉 Done: {url}")

        except Exception as e:
            st.error(f"Failed: {folder}")
            st.error(str(e))

    st.session_state.start_batch = False
    st.session_state.confirmed = False

