from fetch_transcripts import extract_subtitles_from_videos
import pandas as pd

video_ids = ["", ""]
df = extract_subtitles_from_videos(video_ids)
print(df[["video_id", "subtitles"]])
