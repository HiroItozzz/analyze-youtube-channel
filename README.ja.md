## Transcript Analyzer

YouTube の動画 ID から該当 YouTube チャンネルの全動画の統計情報と字幕全文を自動取得し、キーワード分析（医療・法律・日常の意外）を行うツール。
csv 形式で出力します。


### 背景

YouTube チャンネルの運営に関わっていた際に使用したコードを整形しました。
具体的には、「日テレ公式チャンネル」のうち、世界仰天ニュースの動画を対象に、医療・法律・「日常の意外」に関するキーワードで分類を行い、再生回数の傾向を分析する為のものでした。

- 参考画像

  ![スクリーンショット](sample_images/screenshot.png)


## Requirements

- **Python 3.13 以上**
- 主要依存ライブラリ:
  - `pandas >= 2.3`
  - `requests >= 2.32`
  - `yt-dlp >= 2025.11.12`
  - 詳しくは `requirements.txt` を参照

---


## 🚀 クイックスタート

- 必要なライブラリをインストール

```bash
pip install -r requirements.txt
```

- 環境変数を`.env` で設定：

```
YOUTUBE_API_KEY=your_api_key
SUBTITLE_LANGS=ja    # en, ko, zh-Hans etc...
VIDEO_IDS=your_video_id1, your_video_id2,...
TITLE_FILTER=        # ex. 世界仰天ニュース
THRESHOLD=0.5        # 分類のための閾値。単位は1分あたり指定キーワード登場回数
```

- 実行

```bash
python main.py
```

結果は `output/video_analysis_result.csv` へ出力。

---


## 📊 出力形式

`output/video_analysis_result.csv` の主要列：

| 列名                       | 説明                                 |
| -------------------------- | ------------------------------------ |
| `video_id`                 | 動画 ID                              |
| `title`                    | 動画タイトル                         |
| `views`                    | 再生回数　　　　　　　　             |
| `likes`                    | いいね数 　　　　　　　　　　　　    |
| `comments `                | コメント数　　                       |
| `subtitles`                | 字幕テキスト全文                     |
| `medical_word_count`       | 医療キーワード出現回数               |
| `medical_per_min`          | 医療キーワード（1 分あたり）         |
| `is_medical`               | 医療関連判定                         |
| `legal_word_count`         | 法律キーワード出現回数               |
| `legal_per_min`            | 法律キーワード（1 分あたり）         |
| `is_legal`                 | 法律関連判定                         |
| `daily_surprising_per_min` | 日常の意外系キーワード（1 分あたり） |
| `is_daily_surprising`      | 日常の意外判定                       |
| `primary_category`         | 最も関連度が高いカテゴリ             |

---


## 📋 モジュール構成

| ファイル               | 役割                                                  |
| ---------------------- | ----------------------------------------------------- |
| `main.py`              | メイン処理（API 取得 → 字幕取得 → 分析 → csv で保存） |
| `youtube_client.py`    | YouTube Data API 呼び出し + 統計情報取得              |
| `fetch_transcripts.py` | yt-dlp で字幕取得                                     |
| `keywords.py`          | キーワード定義・分析関数                              |

- keywords.py

<img src="sample_images/keywords.png" width="600">

---


## 工夫した点

- `YouTube Data API v3` の扱い
  - YouTube API を叩けば一度でチャンネル全動画のそれぞれの統計情報を取得できるわけではなく、何度かに分けて別のリソースへリクエストを送る必要があり、その方法は複数考えられます。その中で、このコードでは最も取得しやすい動画 ID を入力とし、手軽に使えるようにしています。
  - まず 1 件の動画 ID を使用して `videos` リソースから チャンネル ID（UC-形式）を取得し、そのチャンネルに対応して自動生成される全動画プレイリストの プレイリスト ID（UU-形式）へと文字列で置換します。その後、`playlistItems`リソースから全動画の動画 ID を取得。最後に再び`videos`リソースへリクエストを送ることで、チャンネル全動画の統計情報を効率的に取得するようにしました。

## 学んだこと

- 良いパッケージ管理の方法
- ユーザー定義値を環境変数で設定する方法
- デバッグモードの実装方法
- 具体的なエラーハンドリング
- pytest の使い方
- git の基本的な使い方（コマンド、 .gitignore etc...）
- 

---


## 📚 参考資料

- YouTube Data API: https://developers.google.com/youtube/v3
- yt-dlp: https://github.com/yt-dlp/yt-dlp
