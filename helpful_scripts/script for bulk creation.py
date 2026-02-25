import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ===== CONFIG =====
from pathlib import Path

ROOT_PROJECT = Path(r"E:\Github\auto_video_publisher")
SOURCE_VIDEO_FOLDER = Path(r"C:\Users\Sash\Desktop\whatsapp video")
POSTS_FOLDER = Path(r"E:\Github\auto_video_publisher\posts")
START_OFFSET_DAYS = 1  # start from tomorrow
SCHEDULE_HOUR_UTC = 12  # 12:00 UTC = 5:30 PM IST

TITLES = [
    "घर के कामों में छपी प्रेरणा",
    "स्वर्ग से सुंदर",
    "किस्मत की कुंजी आपके हाथ",
    "अपनी शक्ति को पहचानो",
    "हौसला जो रोक न पाए",
    "सफलता की कुंजी",
    "मायका बुलाया नहीं जाता मोटिवेशन",
    "फोकट की सलाह",
    "आशा की नई किरण",
    "अनुभव सबसे बड़ी दौलत",
    "जवाब दो मर्यादित तरीके से",
    "दोहरी नजर का सच",
    "हर अपना अपना नहीं होता है"
]

COMMON_TAGS = [
    "hindi motivation",
    "motivation for housewives",
    "indian housewife inspiration",
    "daily motivation hindi",
    "women empowerment hindi",
    "ghar ka kaam motivation",
    "motivational shorts hindi",
    "inspiring women stories",
    "family motivation hindi",
    "life lessons hindi"
]

HASHTAGS = "#motivation #hindimotivation #housewifemotivation #dailyinspiration #shorts"

def create_metadata(title, schedule_date):
    return {
        "post_id": title.replace(" ", "_"),
        "publish_to": ["youtube"],
        "youtube": {
            "title": f"{title} | Hindi Motivation Shorts",
            "description": f"{title}\n\nDaily inspiration for every housewife who finds strength in household work.\n\n{HASHTAGS}",
            "tags": COMMON_TAGS,
            "category": "24",
            "privacy": "private",  # keep private if scheduling
            "publish_at": schedule_date,
            "made_for_kids": False,
            "license": "youtube",
            "embeddable": True,
            "public_stats_viewable": True,
            "notify_subscribers": True,
            "playlists": None,
            "use_custom_thumbnail": False,
            "pinned_comment": "If this inspired you, share it with someone who needs it ❤️"
        }
    }

def main():
    POSTS_FOLDER.mkdir(parents=True, exist_ok=True)

    videos = sorted(SOURCE_VIDEO_FOLDER.glob("*.mp4"))

    for index, video_path in enumerate(videos):
        if index >= len(TITLES):
            break

        schedule_day = datetime.now(timezone.utc).date() + timedelta(days=START_OFFSET_DAYS + index)
        publish_datetime = datetime(
            schedule_day.year,
            schedule_day.month,
            schedule_day.day,
            SCHEDULE_HOUR_UTC,
            0,
            0,
            tzinfo=timezone.utc
        )

        schedule_str = publish_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

        post_folder = POSTS_FOLDER / f"reel_{index+1:02d}"
        post_folder.mkdir(parents=True, exist_ok=True)

        # Copy video
        target_video_path = post_folder / "video.mp4"
        with open(video_path, "rb") as src, open(target_video_path, "wb") as dst:
            dst.write(src.read())

        # Create thumbnails folder (empty since we disable custom thumbnail)
        (post_folder / "thumbnails").mkdir(exist_ok=True)
        (post_folder / "processed").mkdir(exist_ok=True)

        metadata = create_metadata(TITLES[index], schedule_str)

        with open(post_folder / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"Created: {post_folder}")

    print("All folders generated successfully!")

if __name__ == "__main__":
    main()