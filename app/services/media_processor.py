from PIL import Image
import os
from app.constants import YOUTUBE_THUMBNAIL_MAX_BYTES

# from moviepy.editor import VideoFileClip


def compress_thumbnail(input_path, output_path):
    img = Image.open(input_path)
    quality = 95

    while quality > 10:
        img.save(output_path, format="JPEG", quality=quality)
        size = os.path.getsize(output_path)

        if size <= YOUTUBE_THUMBNAIL_MAX_BYTES:
            return output_path

        quality -= 5

    raise Exception("Thumbnail cannot be compressed under 2MB.")