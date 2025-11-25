import os
from dotenv import load_dotenv
import requests
import pandas as pd
import isodate
import time
import random

from analyzer import get_all_video_ids, get_playlist_ids, get_video_details
import fetch_transcripts


VIDEO_IDS = ["-4cr9HQ0Uu0"]

load_dotenv()
API_KEY = os.environ["YOUTUBE_API_KEY"]
DEBUG = os.getenv("DEBUG", "False") == "True"


def test_get_channel_ids():
    result = get_playlist_ids(VIDEO_IDS, API_KEY)

    assert len(result) > 0
    assert "playlist_id" in result.columns  # channel_id列がある
    assert result["playlist_id"].iloc[0] != ""  # 値が入っている


def test_get_all_video_ids():
    playlist_ids = get_playlist_ids(VIDEO_IDS, API_KEY)
    result = get_all_video_ids(playlist_ids["playlist_id"].to_list(), API_KEY)

    assert len(result) > 0
    assert "video_id" in result.columns  # video_id列がある
    assert result["video_id"].iloc[0] != ""  # 値が入っている


def test_get_video_details():
    video_ids = get_all_video_ids(
        get_playlist_ids(VIDEO_IDS, API_KEY)["playlist_id"].to_list(), API_KEY
    )
    result = get_video_details(video_ids["video_id"].to_list(), API_KEY)

    assert len(result) > 0
    assert "video_id" in result.columns  # video_id列がある
    assert result["video_id"].iloc[0] != ""  # 値が入っている


def test_extract_subtitles_from_videos():
    result = fetch_transcripts.extract_subtitles_from_videos(VIDEO_IDS)

    assert len(result) > 0
    assert "video_id" in result.columns  # video_id列がある
    assert "subtitles" in result.columns  # subtitles列がある
    assert result["video_id"].iloc[0] != ""  # 値が入っている
    assert result["subtitles"].iloc[0] != ""  # 値が入っている


if __name__ == "__main__":
    # test_get_channel_ids()
    # test_get_all_video_ids()
    # test_get_video_details()
    test_extract_subtitles_from_videos()
    print("All tests passed!")
