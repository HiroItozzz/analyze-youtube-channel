import os
import re
from pathlib import Path
from yt_dlp import YoutubeDL

# --- 設定 ---
# 抽出したい字幕の言語コード（複数指定可能）
SUBTITLE_LANGS = os.getenv("SUBTITLE_LANGS", "ja").split(",")  # 例: ["ja", "en"]
# 字幕ファイルを一時保存するディレクトリ
TMP_SUB_DIR = Path("tmp_subs")

# --- ヘルパー関数 ---


def subtitle_file_to_text(path: Path) -> str:
    """
    SRT/VTTファイルから、タイムスタンプや番号を削除し、純粋なテキストを抽出する
    """
    if not path.exists():
        return ""
    lines_out = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # SRT/VTTの不要な行をスキップ (番号, タイムスタンプ, ヘッダ)
            if (
                not line
                or re.fullmatch(r"\d+", line)
                or re.match(r"^\d{2}:\d{2}:\d{2}[,.]\d{3} --> ", line)
                or line.startswith("WEBVTT")
                or line.startswith("NOTE")
            ):
                continue

            lines_out.append(line)

    # 全てのテキストをスペースで繋げる
    return " ".join(lines_out)


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


def extract_subtitles_from_video(video_url: str) -> str:
    """
    yt-dlpを使用して字幕をファイルにダウンロードし、抽出する
    """

    # URLからvideo_idを抽出 (ファイル名作成用)
    video_id = YoutubeDL({}).extract_info(video_url, download=False)["id"]

    # 既存のキャッシュディレクトリ作成
    TMP_SUB_DIR.mkdir(exist_ok=True, parents=True)

    # yt-dlp オプション: ダウンロードはスキップし、字幕のみを取得
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": SUBTITLE_LANGS,
        "subtitlesformat": "srt/vtt",  # SRT/VTT形式で保存（json3は使用しない）
        # ダウンロード先のファイル名のテンプレート
        "outtmpl": str(TMP_SUB_DIR / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # ★ 確実に動作させるため、字幕ファイルをディスクにダウンロードする
            ydl.download([video_url])

        # ダウンロードされたファイルからテキストを抽出
        sub_path = find_downloaded_subfile(video_id)

        if sub_path:
            text = subtitle_file_to_text(sub_path)
            # 抽出に使ったファイルを削除 (オプション)
            # sub_path.unlink()
            return text

        return ""  # 字幕ファイルが見つからなかった場合

    except Exception as e:
        print(f"字幕の抽出に失敗しました: {e}")
        return ""


# --- 実行例 ---
if __name__ == "__main__":
    # テスト動画ID (字幕が存在する動画に差し替えてください)
    test_video_url = "https://www.youtube.com/watch?v=3jiUMCoLgzI"

    # 実行
    subtitles = extract_subtitles_from_video(test_video_url)

    print("-" * 30)
    print(f"URL: {test_video_url}")
    if subtitles:
        print(f"抽出された字幕 (最初の300文字):\n{subtitles[:300]}...")
    else:
        print("字幕は見つかりませんでした。")
    print("-" * 30)
