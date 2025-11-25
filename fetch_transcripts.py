import os
import re
import shutil
import random, time

from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
from yt_dlp import YoutubeDL


load_dotenv()

# --- 設定 ---
# 抽出したい字幕の言語コード（複数指定可能）
SUBTITLE_LANGS = os.getenv("SUBTITLE_LANGS", "ja").split(",")  # 例: ["ja", "en"]
# 字幕ファイルを一時保存するディレクトリ
TMP_SUB_DIR = Path("tmp_subs")


def subtitle_file_to_text(path: Path) -> str:
    """
    DL済みSRT/VTTファイルから、タイムスタンプや番号を削除し、純粋なテキストを抽出する
    """
    if not path.exists():
        return ""
    lines_out = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # SRT/VTTの不要な行をスキップ (番号, タイムスタンプ, ヘッダ)
            if (
                not line  # 空行
                or re.fullmatch(
                    r"\d+", line
                )  # 行全体が1つ以上の数字のみで構成されている場合
                or re.match(
                    r"^\d{2}:\d{2}:\d{2}[,.]\d{3} --> ", line
                )  # 行の先頭がタイムスタンプ形式で始まっている場合
                or line.startswith("WEBVTT")
                or line.startswith("NOTE")
            ):
                continue  # はスキップ

            lines_out.append(line)

    return "".join(lines_out)


def find_downloaded_subfile(video_id: str) -> Path | None:
    """
    一時ディレクトリから、指定言語の字幕ファイルを探す
    """
    for lang in SUBTITLE_LANGS:
        for ext in ("srt", "vtt"):
            p = TMP_SUB_DIR / f"{video_id}.{lang}.{ext}"
            if p.exists():
                return p
    return None


def extract_subtitles_from_videos(video_ids: list[str]) -> pd.DataFrame:
    """
    字幕をダウンロードし、抽出
    """
    data = []

    for video_id in video_ids:
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # キャッシュディレクトリ作成
        TMP_SUB_DIR.mkdir(exist_ok=True, parents=True)

        # yt-dlp オプション: ダウンロードはスキップし、字幕のみを取得
        ydl_opts = {
            "skip_download": True,  # 動画本体はダウンロードしない
            "writesubtitles": True,  # 字幕をダウンロードする
            "writeautomaticsub": True,  # 自動生成字幕もダウンロードする
            "subtitleslangs": SUBTITLE_LANGS,  # 指定言語の字幕を取得
            "subtitlesformat": "srt/vtt",  # 字幕フォーマット
            "outtmpl": str(
                TMP_SUB_DIR / "%(id)s.%(ext)s"
            ),  # 保存パスとファイル名のテンプレート
            "quiet": True,  # ログを抑制
            "no_warnings": True,  # 警告を抑制
            "ignoreerrors": True,  # エラーを無視して続行
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            sub_path = find_downloaded_subfile(video_id)

            subtitles = subtitle_file_to_text(sub_path) if sub_path else ""
            data.append({"video_id": video_id, "subtitles": subtitles})

            if not sub_path:
                print(f"{video_id}の字幕が見つかりませんでした。")

        except Exception as e:
            print(f"{video_id}の字幕の抽出に失敗しました: {e}")

        # YouTube APIのレート制限を回避するため待機
        time.sleep(random.uniform(0.5, 1.5))

    df = pd.DataFrame(data)
    return df


def delete_temp_directory(temp_dir: Path):
    """
    一時ディレクトリを全て削除する
    """
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            print(f"\n 一時ディレクトリ {temp_dir} を削除しました。")
        except OSError as e:
            print(f"\n 警告: 一時ディレクトリの削除に失敗しました: {e}")


if __name__ == "__main__":
    # テスト動画ID (字幕が存在する動画に差し替えてください)
    test_video_ids = ["tnDeaea4cGk"]
    try:
        # execute
        df = extract_subtitles_from_videos(test_video_ids)

        print("-" * 30)
        print(f"video_id: {test_video_ids}")
        if df:
            print(f"抽出された字幕:\n{df[["video_id", "subtitles"]]}...")
        print("-" * 30)

    finally:
        # 処理が成功しても失敗しても、最後にフォルダを削除する
        delete_temp_directory(TMP_SUB_DIR)
