from app.models import metadata
from app.models.post import Post
from app.services.validator import validate_youtube_metadata
from app.services.media_processor import compress_thumbnail
from app.platforms.youtube import YouTubePlatform
from app.services.excel_logger import log_to_excel


def run_pipeline(folder_path, credentials_path, platforms, skip_validation, step_callback=None):
    def update(step, status):
        if step_callback:
            step_callback(step, status)

    # STEP 1
    update("Loading Post", "running")
    post = Post(folder_path)
    update("Loading Post", "done")

    # STEP 2
    update("Validating Metadata", "running")
    yt_metadata = post.get_youtube_metadata()
    validate_youtube_metadata(yt_metadata)
    update("Validating Metadata", "done")

    

    if yt_metadata.get("use_custom_thumbnail", True):
    
        # STEP 3
        update("Compressing Thumbnail", "running")
        thumbnail_input = list(post.thumbnail_folder.glob("*"))[0]
        output_path = post.processed_folder / "yt_thumbnail.jpg"
        compress_thumbnail(thumbnail_input, output_path)
        update("Compressing Thumbnail", "done")

    # STEP 4
    update("Authenticating YouTube", "running")
    youtube = YouTubePlatform(credentials_path)
    youtube.authenticate()
    update("Authenticating YouTube", "done")

    # STEP 5
    update("Uploading Video", "running")

    def yt_progress(percent):
        update("Uploading Video", percent)

    video_id = youtube.upload_video(post, progress_callback=yt_progress)

    update("Uploading Video", "done")

    if yt_metadata.get("use_custom_thumbnail", True):
        # STEP 6
        update("Uploading Thumbnail", "running")
        youtube.upload_thumbnail(video_id, str(output_path))
        update("Uploading Thumbnail", "done")


    # Playlist automation
    if yt_metadata.get("playlists"):
        youtube.add_to_playlists(video_id, yt_metadata["playlists"])

    # Post comment
    # if yt_metadata.get("pinned_comment"):
    #     youtube.post_comment(video_id, yt_metadata["pinned_comment"])
    #     # STEP 7
    update("Logging to Excel", "running")
    video_url = f"https://youtube.com/watch?v={video_id}"
    log_to_excel(post.metadata["post_id"], "YouTube", "Success", video_url)
    update("Logging to Excel", "done")

    return video_url