import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.services.auth_manager import get_youtube_credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]


class YouTubePlatform:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.token_path = credentials_path.replace(
            "youtube.json", "youtube_token.json"
        )
        self.service = None

    def authenticate(self):
        creds = get_youtube_credentials(
            self.credentials_path,
            self.token_path
        )
        self.service = build("youtube", "v3", credentials=creds)

    # -------------------------------------------------
    # VIDEO UPLOAD (FULL FEATURE SUPPORT)
    # -------------------------------------------------
    def upload_video(self, post, progress_callback=None):
        metadata = post.get_youtube_metadata()

        status_data = {
            "privacyStatus": metadata.get("privacy", "private"),
            "selfDeclaredMadeForKids": metadata.get("made_for_kids", False),
            "license": metadata.get("license", "youtube"),
            "embeddable": metadata.get("embeddable", True),
            "publicStatsViewable": metadata.get("public_stats_viewable", True),
        }

        if metadata.get("publish_at"):
            status_data["publishAt"] = metadata["publish_at"]

        snippet_data = {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("tags", []),
            "categoryId": metadata.get("category", "22"),
            "defaultLanguage": metadata.get("default_language", "en"),
            "defaultAudioLanguage": metadata.get(
                "default_audio_language", "en"
            ),
        }

        request_body = {
            "snippet": snippet_data,
            "status": status_data,
        }

        media = MediaFileUpload(
            str(post.video_path),
            chunksize=1024 * 1024,
            resumable=True
        )

        request = self.service.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media,
            notifySubscribers=metadata.get("notify_subscribers", True),
        )

        response = None

        while response is None:
            status, response = request.next_chunk()

            if status and progress_callback:
                percent = int(status.progress() * 100)
                progress_callback(percent)

        return response["id"]

    # -------------------------------------------------
    # THUMBNAIL
    # -------------------------------------------------
    def upload_thumbnail(self, video_id, thumbnail_path):
        self.service.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path),
        ).execute()

    # -------------------------------------------------
    # PLAYLIST AUTOMATION
    # -------------------------------------------------
    def add_to_playlists(self, video_id, playlist_ids):
        for playlist_id in playlist_ids:
            try:
                self.service.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                ).execute()
            except Exception as e:
                print(f"Playlist failed: {playlist_id}")
                print(e)
    # -------------------------------------------------
    # POST COMMENT (PIN MANUALLY LATER)
    # -------------------------------------------------
    def post_comment(self, video_id, text):
        self.service.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": text
                        }
                    }
                }
            }
        ).execute()