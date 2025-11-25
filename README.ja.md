```markdown
# Transcript Analyzer

YouTube 動画の字幕を取得し、キーワード分析（医療・法律・日常の意外）を行うツール。

**想定チャンネル:** 日テレ公式チャンネル（世界仰天ニュース）

---

## 🚀 クイックスタート

```bash
python main.py
```

結果は `output/video_analysis_result.csv` に保存されます。

---

## 📋 モジュール構成

| ファイル               | 役割                                            |
| ---------------------- | ----------------------------------------------- |
| `main.py`              | メイン処理（API 取得 → 字幕取得 → 分析 → 保存） |
| `analyzer.py`          | YouTube Data API 呼び出し                       |
| `fetch_transcripts.py` | yt-dlp で字幕ダウンロード                       |
| `keywords.py`          | キーワード定義・分析関数                        |

---

## 🔤 Keywords モジュール

### インポート方法

```python
# 関数をインポート（最も簡単）
from keywords import analyze_by_keywords, count_keywords_in_category, is_category

# キーワード辞書をインポート
from keywords import KEYWORD_CATEGORIES, medical_keywords, legal_keywords, daily_surprising_keywords
```

### よく使う関数

**1. `is_category(text, category)` → True/False**

```python
if is_category("医師が重症を診断した", "medical"):
    print("医療関連")
```

**2. `count_keywords_in_category(text, category)` → 出現回数**

```python
count = count_keywords_in_category("病気で入院して治療を受けた", "medical")
# → 3
```

**3. `analyze_by_keywords(df, category, threshold=0.5)` → DataFrame 修正（インプレイス）**

```python
# DataFrame に以下の列を追加:
# - {category}_word_count
# - {category}_per_min (1分あたりのキーワード出現数)
# - is_{category} (threshold 以上なら True)
analyze_by_keywords(df, "medical", threshold=0.5)
```

### 使えるカテゴリ

- `"medical"` → 医療関連
- `"legal"` → 法律・犯罪
- `"daily_surprising"` → 日常の意外な出来事

---

## 📊 出力形式

`output/video_analysis_result.csv` の主要列：

| 列名                       | 説明                         |
| -------------------------- | ---------------------------- |
| `video_id`                 | 動画 ID                      |
| `title`                    | 動画タイトル                 |
| `transcript`               | 字幕テキスト                 |
| `medical_word_count`       | 医療キーワード出現回数       |
| `medical_per_min`          | 医療キーワード（1 分あたり） |
| `is_medical`               | 医療関連判定                 |
| `legal_word_count`         | 法律キーワード出現回数       |
| `legal_per_min`            | 法律キーワード（1 分あたり） |
| `is_legal`                 | 法律関連判定                 |
| `daily_surprising_per_min` | 日常の意外（1 分あたり）     |
| `is_daily_surprising`      | 日常の意外判定               |
| `primary_category`         | 最も関連度が高いカテゴリ     |

---

## 🔧 カスタマイズ

### 環境変数

`.env` で設定：

```
YOUTUBE_API_KEY=your_api_key
DEBUG=False
```

### 分析対象チャンネル変更

`main.py` の `VIDEO_IDS` を変更：

```python
VIDEO_IDS = ["YOUR_CHANNEL_VIDEO_ID"]
```

### 出力先変更

`main.py` の `OUTPUT_DIR` を変更：

```python
OUTPUT_DIR = Path("your_output_directory")
```

---

## 📝 使用例

### 基本的な分析

```python
import pandas as pd
from keywords import analyze_by_keywords, count_keywords_in_category

df = pd.DataFrame({
    'video_id': ['vid001'],
    'transcript': ['医師が重症の病気を診断した'],
    'duration': [900]  # 秒単位
})

# 医療分析
analyze_by_keywords(df, "medical")
print(df[['video_id', 'medical_per_min', 'is_medical']])
```

### 複数カテゴリ分析

```python
from keywords import KEYWORD_CATEGORIES, analyze_by_keywords

for category in KEYWORD_CATEGORIES.keys():
    analyze_by_keywords(df, category=category, threshold=0.5)
```

---

## 🐛 トラブルシューティング

| 問題                     | 原因                 | 解決策                                                               |
| ------------------------ | -------------------- | -------------------------------------------------------------------- |
| 字幕が空                 | ダウンロード失敗     | `tmp_subs/` を確認、`find_downloaded_subfile()` の引数をリストで渡す |
| キーワードが検出されない | threshold が高すぎる | threshold を下げる（デフォルト 0.5）                                 |
| API エラー               | レート制限           | `analyzer.py` の `time.sleep()` を増やす                             |

---

## 📚 参考資料

- YouTube Data API: https://developers.google.com/youtube/v3
- yt-dlp: https://github.com/yt-dlp/yt-dlp

```
