from pathlib import Path
import json


class Post:
    def __init__(self, folder_path: str):
        self.folder = Path(folder_path)
        self.video_path = None
        self.thumbnail_folder = None
        self.processed_folder = self.folder / "processed"
        self.metadata = None

        self._load_structure()

    def _load_structure(self):
        # Video
        videos = list(self.folder.glob("*.mp4"))
        if not videos:
            raise Exception("No video file found.")
        self.video_path = videos[0]

        # Thumbnails
        self.thumbnail_folder = self.folder / "thumbnails"
        if not self.thumbnail_folder.exists():
            raise Exception("Thumbnails folder missing.")

        # Metadata
        metadata_file = self.folder / "metadata.json"
        if not metadata_file.exists():
            raise Exception("metadata.json missing.")

        with open(metadata_file, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.processed_folder.mkdir(exist_ok=True)

    def get_youtube_metadata(self):
        return self.metadata.get("youtube", {})