## Transcript Analyzer

A small toolkit to download YouTube subtitles and perform keyword-based analysis focused on three categories: medical, legal/crime, and surprising daily events. It was originally developed for the Japanese TV program "Sekai Gyoten News" (世界仰天ニュース), but works for any channel.

### Quick start

Run the main script:

```pwsh
python main.py
```

Output CSV will be written to the `output/` directory (e.g. `output/video_analysis_result.csv`).

### Project layout

- `main.py` - Main pipeline (API -> subtitles -> analysis -> save)
- `analyzer.py` - YouTube Data API helper functions
- `fetch_transcripts.py`- Download and extract subtitles via `yt-dlp`
- `keywords.py` - Keyword lists and analysis utilities

### Keywords module (usage)

You can import helper functions directly:

```python
from keywords import analyze_by_keywords, count_keywords_in_category, is_category
from keywords import KEYWORD_CATEGORIES
```

- `is_category(text, category)` -> boolean: whether any keyword in `category` appears in `text`.
- `count_keywords_in_category(text, category)` -> int: raw count of keyword occurrences.
- `analyze_by_keywords(df, category, threshold=0.5)` -> modifies DataFrame in-place and adds columns:
  - `{category}_word_count`
  - `duration_min` (if missing)
  - `{category}_per_min` (keywords per minute, rounded)
  - `is_{category}` (True if `per_min >= threshold`)

Available categories: `medical`, `legal`, `daily_surprising`.

### Title keyword flags

`add_title_keyword_flags(df, category)` will add `{category}_in_title` (boolean) indicating whether any keyword appears in the video title.

### Output columns (example)

The CSV contains the original metadata plus analysis columns, for example:

```
video_id,title,transcript,duration,medical_word_count,medical_per_min,is_medical,medical_in_title,...,primary_category
```

### Configuration

Set environment variables in a `.env` file:

```
YOUTUBE_API_KEY=your_api_key
DEBUG=False
```

To change the videos being analyzed, edit `VIDEO_IDS` in `main.py`.

### Examples

Single-video analysis example:

```python
import pandas as pd
from keywords import analyze_by_keywords

df = pd.DataFrame({
    'video_id': ['vid001'],
    'transcript': ['The doctor diagnosed a serious illness.'],
    'duration': [900]  # seconds
})

analyze_by_keywords(df, 'medical')
print(df[['video_id','medical_per_min','is_medical']])
```

Multiple-category loop:

```python
from keywords import KEYWORD_CATEGORIES, analyze_by_keywords

for category in KEYWORD_CATEGORIES.keys():
    analyze_by_keywords(df, category=category, threshold=0.5)
```

### Troubleshooting

- Empty subtitles: check `tmp_subs/` and ensure `find_downloaded_subfile()` is used correctly.
- No keywords detected: try lowering the `threshold` (default 0.5 per minute).
- API errors / rate limits: increase `time.sleep()` in `analyzer.py`.

### Dependencies

See `requirements.in` and `requirements.txt`. Main runtime dependencies include `pandas`, `python-dotenv`, `requests`, `isodate`, and `yt-dlp`.

### References

- YouTube Data API: https://developers.google.com/youtube/v3
- yt-dlp: https://github.com/yt-dlp/yt-dlp
