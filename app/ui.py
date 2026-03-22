import sys
import os
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from app.pipeline import run_pipeline
  # Log special status instead of Success
from app.services.excel_logger import log_to_excel

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
import pandas as pd
from datetime import datetime

UPLOAD_LOG_PATH = r"E:\Github\auto_yt_uploader\output\publishing_history.xlsx"


def extract_post_id_from_folder(folder_name):
    parts = folder_name.split("_", 2)
    if len(parts) >= 3:
        return parts[2]
    return None


def extract_datetime_from_folder(folder_name):
    try:
        date_part, time_part, _ = folder_name.split("_", 2)
        dt_str = f"{date_part} {time_part.replace('-', ':')}"
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except Exception:
        return datetime.min



# LOAD SUCCESSFULLY UPLOADED POST IDs

processed_ids = set()

if os.path.exists(UPLOAD_LOG_PATH):
    try:
        df = pd.read_excel(UPLOAD_LOG_PATH)

        # Only hide posts that were successfully uploaded
        if {"Post ID", "Status"}.issubset(df.columns):
            success_df = df[df["Status"] == "Success"]
            processed_ids = set(
                success_df["Post ID"].dropna().astype(str)
            )

    except Exception:
        # If Excel is corrupted or open, don't block UI
        processed_ids = set()

# DETECT NEW POST FOLDERS

all_folders = []

for p in Path(posts_root).iterdir():
    if p.is_dir():
        folder_name = p.name
        post_id = extract_post_id_from_folder(folder_name)

        # Show only folders not successfully uploaded
        if post_id and post_id not in processed_ids:
            folder_dt = extract_datetime_from_folder(folder_name)
            all_folders.append((p.name, str(p), folder_dt))

# SORT NEWEST FIRST

all_folders_sorted = sorted(
    all_folders,
    key=lambda x: x[2],
    # reverse=True
)

# CLEAN UI DISPLAY

folder_name_map = {
    name: full_path
    for name, full_path, _ in all_folders_sorted
}

all_post_folders = list(folder_name_map.keys())

if not all_post_folders:
    st.info("No new posts to publish 🎉")
    st.stop()

selected_folder_names = st.multiselect(
    "Select Post Folders to Process",
    all_post_folders
)

selected_folders = [
    folder_name_map[name]
    for name in selected_folder_names
]

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
            error_message = str(e)

            # Detect YouTube daily upload limit
            if "uploadLimitExceeded" in error_message:
                st.warning("⚠ Daily YouTube upload limit reached.")
                st.warning("Uploads will be available again in ~24 hours.")


                post_id = Path(folder).name.split("_", 2)[2]

                log_to_excel(
                    post_id=post_id,
                    platform="YouTube",
                    status="LimitReached",
                    url="N/A",
                    metadata=None
                )

                break  # Stop processing remaining folders

            else:
                st.error(f"Failed: {folder}")
                st.error(error_message)

    st.session_state.start_batch = False
    st.session_state.confirmed = False
