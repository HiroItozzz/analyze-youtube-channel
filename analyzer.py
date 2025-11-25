import os
from dotenv import load_dotenv
import requests
import pandas as pd
import isodate
import time
import random

VIDEO_IDS = ["SyibOFcjCHk"]

load_dotenv()
API_KEY = os.environ["YOUTUBE_API_KEY"]
SUBTITLE_LANGS = os.getenv("SUBTITLE_LANGS", "ja")  # default to Japanese
DEBUG = os.getenv("DEBUG", "False") == "True"

if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY is not set. Please check your .env file.")

if DEBUG:
    print(f"API Key loaded: {API_KEY[:10]}...")


def get_playlist_ids(video_ids: list[str], api_key: str):
    """Get the channel ID (UC~~)
    →→→ convert it to the automatically generated playlist ID (UU~~) of all videos on the channel
    """

    base_url = "https://www.googleapis.com/youtube/v3/videos"
    playlist_ids = []

    if DEBUG:
        print(f"Processing started: {len(video_ids)} items")

    for i in range(0, len(video_ids), 50):
        ids = ",".join(video_ids[i : i + 50])
        url = f"{base_url}?part=snippet&id={ids}&key={api_key}"

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            print(f"API call error: {e}")
            print("Could not retrieve data for video IDs:", ids)
            continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            continue

        if DEBUG:
            print(f"API call completed! Video IDs: {ids}")

        for item in data["items"]:
            playlist_id = item.get("snippet", {}).get("channelId", "")
            if playlist_id:
                playlist_id = playlist_id.replace(
                    "C", "U", 1
                )  # converting "UU~~" to "UC~~"
            playlist_ids.append({"playlist_id": playlist_id})

        time.sleep(random.uniform(0.1, 0.2))

    df = pd.DataFrame(playlist_ids).drop_duplicates()

    if DEBUG:
        print(f"Processing finished: {len(df)} items")

    return df


def get_all_video_ids(playlist_ids: list[str], api_key: str) -> pd.DataFrame:
    base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    videos = []
    if DEBUG:
        print(f"Processing started: {len(playlist_ids)} items")

    for playlist_id in playlist_ids:
        next_page_token = None

        while True:
            url = (
                f"{base_url}?part=snippet&playlistId={playlist_id}&maxResults=50"
                f"&pageToken={next_page_token or ''}&key={api_key}"
            )

            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()

            except requests.exceptions.RequestException as e:
                print(f"API call error: {e}")
                print("could not retrieve data for playlist ID:", playlist_id)
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

            if DEBUG:
                print(f"API call completed! Playlist ID: {playlist_id}")

            for item in data["items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                videos.append({"video_id": video_id})

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
            time.sleep(random.uniform(0.1, 0.2))

    if DEBUG:
        print(f"Processing finished: {len(videos)} items")

    return pd.DataFrame(videos)


def get_video_details(video_ids: list[str], api_key) -> pd.DataFrame:
    """Get detailed information from video ID list"""

    base_url = "https://www.googleapis.com/youtube/v3/videos"
    all_data = []

    for i in range(0, len(video_ids), 50):
        ids = ",".join(video_ids[i : i + 50])
        url = (
            f"{base_url}?part=snippet,contentDetails,statistics&id={ids}&key={api_key}"
        )
        resp = requests.get(url).json()

        for item in resp["items"]:
            vid = item["id"]
            title = item["snippet"]["title"]
            published_at = item["snippet"]["publishedAt"][:10]
            duration = item["contentDetails"]["duration"]  # ISO 8601 (PTxxMxxS)
            stats = item.get("statistics", {})
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            url_video = f"https://www.youtube.com/watch?v={vid}"

            published_date = pd.to_datetime(published_at, utc=True).date()
            duration_sec = int(
                isodate.parse_duration(duration).total_seconds()
            )  # convert to seconds

            all_data.append(
                [
                    vid,
                    title,
                    published_date,
                    views,
                    duration_sec,
                    likes,
                    comments,
                    url_video,
                ]
            )

    # duration is standardized to 'duration' (seconds) for downstream consistency
    df = pd.DataFrame(
        all_data,
        columns=[
            "video_id",
            "title",
            "date",
            "views",
            "duration",
            "likes",
            "comments",
            "URL",
        ],
    )
    return df


if __name__ == "__main__":
    playlist_ids = get_playlist_ids(VIDEO_IDS, API_KEY)
    print(playlist_ids)
    all_videos = get_all_video_ids(playlist_ids["playlist_id"].to_list(), API_KEY)
    print(all_videos.iloc[:10], f"length: {len(all_videos)}")
    video_details = get_video_details(all_videos["video_id"].to_list(), API_KEY)
    print(video_details.iloc[:10], f": {len(video_details)}")
