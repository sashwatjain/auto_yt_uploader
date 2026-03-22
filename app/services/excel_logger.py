import pandas as pd
from pathlib import Path
from datetime import datetime

EXCEL_PATH = Path(r"E:\Github\auto_yt_uploader\output\publishing_history.xlsx")


def log_to_excel(post_id, platform, status, url, metadata=None):

    # -----------------------------
    # Base data (always saved)
    # -----------------------------
    row_data = {
        "Post ID": post_id,
        "Platform": platform,
        "Status": status,
        "URL": url,
        "Logged At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # -----------------------------
    # Add YouTube metadata (optional)
    # -----------------------------
    if metadata:
        row_data.update({
            "Title": metadata.get("title"),
            "Description": metadata.get("description"),
            "Tags": ", ".join(metadata.get("tags", [])),
            "Category": metadata.get("category"),
            "Privacy": metadata.get("privacy"),
            "Publish At (UTC)": metadata.get("publish_at"),
            "Publish At (IST)": metadata.get("publish_at_ist"),
            "Made For Kids": metadata.get("made_for_kids"),
            "License": metadata.get("license"),
            "Embeddable": metadata.get("embeddable"),
            "Public Stats Viewable": metadata.get("public_stats_viewable"),
            "Notify Subscribers": metadata.get("notify_subscribers"),
            "Playlists": ", ".join(metadata.get("playlists", [])) if metadata.get("playlists") else None,
            "Use Custom Thumbnail": metadata.get("use_custom_thumbnail"),
            "Pinned Comment": metadata.get("pinned_comment"),
        })

    new_row = pd.DataFrame([row_data])

    try:
        if EXCEL_PATH.exists():

            existing = pd.read_excel(EXCEL_PATH)

            # 🔥 Align columns safely
            all_columns = list(set(existing.columns).union(set(new_row.columns)))

            existing = existing.reindex(columns=all_columns)
            new_row = new_row.reindex(columns=all_columns)

            updated = pd.concat([existing, new_row], ignore_index=True)

        else:
            updated = new_row

        updated.to_excel(EXCEL_PATH, index=False)

    except Exception as e:
        print("Excel logging failed:", e)
        raise