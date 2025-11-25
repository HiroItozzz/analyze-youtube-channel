## Transcript Analyzer

A tool that retrieves statistical information and subtitles for all videos of the corresponding YouTube channel from the video ID, and performs keyword analysis (medical, legal, everyday unexpected).
Output in csv format.

日本語版 README も参照してください: [README.ja.md](README.ja.md)

- sample image

  ![screenshot](sample_images/screenshot.png)

## Requirements


- **Python 3.13 or higher**
- Main dependent libraries:
- `yt-dlp >= 2025.11.12`
- `requests >= 2.32`
- `pandas >= 2.3`
- See `requirements.txt` for details

---


## 🚀 Quick start

- Install required libraries

```bash
pip install -r requirements.txt
```

- Set environment variables in `.env`:

```
YOUTUBE_API_KEY=your_api_key
SUBTITLE_LANGS=ja     # en, ko, zh-Hans etc...
VIDEO_IDS=your_video_id1, your_video_id2,...
TITLE_FILTER=title_keyword_filter
THRESHOLD=0.5         # Threshold for classification. Unit is specified as the number of keyword appearances per minute
```

- execute

```bash
python main.py
```

The results are saved in `output/video_analysis_result.csv`.

---


## 📊 Output format

Main columns of `output/video_analysis_result.csv`:

| Column name                | Description                                       |
| -------------------------- | ------------------------------------------------- |
| `video_id`                 | Video ID                                          |
| `title`                    | Video title                                       |
| `views`                    | Number of views                                   |
| `likes`                    | Number of likes 　 　 　 　 　 　 　 　 　        |
| `comments `                | Number of comments                                |
| `subtitles`                | Full text of subtitles                            |
| `medical_word_count`       | Number of medical keyword appearances             |
| `medical_per_min`          | Medical keywords (per minute)                     |
| `is_medical`               | Medical-related judgment                          |
| `legal_word_count`         | Number of legal keyword appearances               |
| `legal_per_min`            | Legal keywords (per minute)                       |
| `is_legal`                 | Legal-related judgment                            |
| `daily_surprising_per_min` | Surprising keywords in everyday life (per minute) |
| `is_daily_surprising`      | Daily surprise judgment                           |
| `primary_category`         | Most relevant category                            |

---


## 📋 Module configuration

| File                   | Role                                                                              |
| ---------------------- | --------------------------------------------------------------------------------- |
| `main.py`              | Main processing (API acquisition → subtitle acquisition → analysis → save as csv) |
| `youtube_client.py`    | YouTube Data API call + statistics information acquisition                        |
| `fetch_transcripts.py` | Get subtitles with yt-dlp                                                         |
| `keywords.py`          | Keyword definition/analysis functions                                             |

- keywords.py

<img src="sample_images/keywords.png" width="600">

---


## Technical considerations

- Handling YouTube DATA API
  - It is not possible to obtain statistical information for all videos on a channel at once by calling the YouTube API, but it is necessary to send requests to different resources several times, and there are multiple ways to do this. Among them, this code uses the video ID that is easiest to obtain as input, making it easy to use.
  - First, use one video ID to get the channel ID (UC-format) from the `videos` resource, and replace it with a string with the playlist ID (UU-format) of all video playlists automatically generated for that channel. Then, get the video IDs of all videos from the `playlistItems` resource. Finally, by sending a request to the `videos` resource again, we get the statistics for all videos on the channel.

---


## 📚 Reference materials

- YouTube Data API: https://developers.google.com/youtube/v3
- yt-dlp: https://github.com/yt-dlp/yt-dlp
