import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import isodate

import analyzer, fetch_transcripts
from keywords import analyze_by_keywords, add_title_keyword_flags, KEYWORD_CATEGORIES

VIDEO_IDS = ["CuNik7M56UM"]

load_dotenv()
API_KEY = os.environ["YOUTUBE_API_KEY"]
SUBTITLE_LANGS = os.getenv("SUBTITLE_LANGS", "ja")  # default to Japanese
DEBUG = os.getenv("DEBUG", "False") == "True"

# 出力ディレクトリ設定
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def convert_duration_to_seconds(duration_iso: str) -> int:
    """ISO 8601 形式の duration を秒に変換
    例: "PT15M33S" -> 933
    """
    try:
        return int(isodate.parse_duration(duration_iso).total_seconds())
    except Exception:
        return 0


def analyze_keywords(df: pd.DataFrame) -> pd.DataFrame:
    """
    キーワード分析を実行して DataFrame を返す（保存なし）

    get_youtube_data.ipynb のロジックを踏襲
    """

    # 1. duration を秒からそのまま使用（既に get_video_details で秒単位のはず）
    # もしISO 8601形式なら変換
    if df["duration"].dtype == "object":
        df["duration"] = df["duration"].apply(convert_duration_to_seconds)

    # 2. 全カテゴリで分析（トランスクリプトとタイトル）
    for category in KEYWORD_CATEGORIES.keys():
        print(f"  分析中: {category}")
        analyze_by_keywords(df, category=category, threshold=0.5)
        add_title_keyword_flags(df, category=category)

    # 3. 主要カテゴリを決定（最も出現回数が多いカテゴリ）
    def get_primary_category(row):
        """各行で最も該当度が高いカテゴリを返す"""
        scores = {}
        for category in KEYWORD_CATEGORIES.keys():
            col = f"{category}_per_min"
            scores[category] = row.get(col, 0)
        return (
            max(scores, key=scores.get)
            if max(scores.values(), default=0) > 0
            else "none"
        )

    df["primary_category"] = df.apply(get_primary_category, axis=1)

    return df


def save_to_csv(df: pd.DataFrame, output_path: Path):
    """
    分析結果を CSV に保存

    Args:
        df: 分析済み DataFrame
        output_path: 出力ファイルパス
    """
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✓ 分析結果を保存: {output_path}")


def analyze_and_save(df: pd.DataFrame, output_path: Path):
    """
    キーワード分析を実行してCSVに出力

    get_youtube_data.ipynb のロジックを踏襲
    """

    # 1. duration を秒からそのまま使用（既に get_video_details で秒単位のはず）
    # もしISO 8601形式なら変換
    if df["duration"].dtype == "object":
        df["duration"] = df["duration"].apply(convert_duration_to_seconds)

    # 2. 全カテゴリで分析
    for category in KEYWORD_CATEGORIES.keys():
        print(f"  分析中: {category}")
        analyze_by_keywords(df, category=category, threshold=0.5)

    # 3. 主要カテゴリを決定（最も出現回数が多いカテゴリ）
    def get_primary_category(row):
        """各行で最も該当度が高いカテゴリを返す"""
        scores = {}
        for category in KEYWORD_CATEGORIES.keys():
            col = f"{category}_per_min"
            scores[category] = row.get(col, 0)
        return (
            max(scores, key=scores.get)
            if max(scores.values(), default=0) > 0
            else "none"
        )

    df["primary_category"] = df.apply(get_primary_category, axis=1)

    # 4. CSV に保存
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✓ 分析結果を保存: {output_path}")

    return df


if __name__ == "__main__":
    print("=" * 60)
    print("YouTubeチャンネル分析パイプライン")
    print("=" * 60)

    # Step 1: プレイリストID取得
    print("\n[1] プレイリストID取得中...")
    playlist_data = analyzer.get_playlist_ids(VIDEO_IDS, API_KEY)
    if DEBUG:
        print("Playlist Data:")
        print(playlist_data)

    # Step 2: 全動画ID取得
    print("[2] 全動画ID取得中...")
    playlist_ids = playlist_data["playlist_id"].tolist()
    all_videos_data = analyzer.get_all_video_ids(playlist_ids, API_KEY)
    if DEBUG:
        print("All Videos Data:")
        print(all_videos_data)

    # Step 3: 動画詳細情報取得
    print("[3] 動画詳細情報取得中...")
    all_video_ids = all_videos_data["video_id"].tolist()
    df_video_details = analyzer.get_video_details(all_video_ids, API_KEY)
    if DEBUG:
        print("Video Details:")
        print(df_video_details)

    # Step 4: 字幕取得
    print("[4] 字幕ダウンロード中...")
    df_subtitles = fetch_transcripts.extract_subtitles_from_videos(all_video_ids)

    # Step 5: データ統合
    print("[5] データ統合中...")
    result = pd.merge(df_video_details, df_subtitles, on="video_id", how="outer")
    if DEBUG:
        result.to_csv(
            OUTPUT_DIR / "debug_merged_data.csv",
            index=False,
            encoding="utf-8-sig",
        )

    print(f"  統合行数: {len(result)}")

    # Step 6: キーワード分析 & CSV出力
    print("[6] キーワード分析中...")
    result_analyzed = analyze_keywords(result)

    # Step 7: CSV に保存
    print("[7] 結果を保存中...")
    save_to_csv(result_analyzed, OUTPUT_DIR / "video_analysis_result.csv")

    print("\n" + "=" * 60)
    print("分析完了")
    print("=" * 60)

    # サマリー表示
    print("\n【分析結果サマリー】")
    if not result_analyzed.empty:
        print(
            result_analyzed[
                [
                    "video_id",
                    "title",
                    "medical_per_min",
                    "legal_per_min",
                    "daily_surprising_per_min",
                    "primary_category",
                ]
            ].head(10)
        )

    print(f"\n出力ファイル: {OUTPUT_DIR / 'video_analysis_result.csv'}")
