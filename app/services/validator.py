def validate_youtube_metadata(metadata):
    required = ["title", "description"]

    for field in required:
        if field not in metadata:
            raise Exception(f"Missing field: {field}")

    if len(metadata["title"]) > 100:
        raise Exception("YouTube title too long.")