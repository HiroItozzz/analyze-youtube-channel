from fetch_transcripts import extract_subtitles_from_videos
import pandas as pd

video_ids = ["3jiUMCoLgzI", "tnDeaea4cGk"]  # 字幕がある動画IDに置き換え
df = extract_subtitles_from_videos(video_ids)
print(df[["video_id", "subtitles"]])
