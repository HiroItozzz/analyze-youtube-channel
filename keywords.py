# fmt: off

"""
キーワード集: 世界仰天ニュース分類用

医療、法律、日常の意外な出来事を分類するためのキーワード辞書
"""

medical_keywords = [
    "病気","医療","治療","難病","がん","ガン","癌","感染症","手術","症状","薬","病院",
    "発熱","咳","喘息","糖尿病","高血圧","心臓","脳卒中","認知症",
    "アレルギー","感冒","肝臓","腎臓","骨折","腫瘍","感染","コロナ","インフル",
    "花粉症","検診","検査","MRI","CT","内視鏡","注射","輸血","麻酔","投薬","診断",
    "医師","看護","救急","救命","クリニック","医大","ワクチン","リハビリ","食中毒",
    "重症","軽症","腹痛","命に関わる","死に至るケース","意識不明","生死の境をさまよう",
    "入院","退院","発症","ウイルス","菌","細菌","免疫","炎症","完治","回復"
]

# ============================================
# 法律・犯罪関連キーワード
# ============================================
legal_keywords = {
    # 犯罪類型
    "殺人", "殺害", "傷害", "暴力", "暴行", "強盗", "窃盗", "盗難", "詐欺", "横領",
    # 性犯罪
    "レイプ", "強制わいせつ", "児童虐待", "痴漢", "ストーキング",
    # 薬物関連
    "麻薬", "覚醒剤", "大麻", "違法薬物",
    # 法的用語
    "逮捕", "起訴", "容疑者", "被告", "判決", "有罪", "無罪", "懲役", "罰金",
    "弁護士", "検察", "裁判", "裁判所", "法廷", "法律", "違法", "犯罪",
    # 交通・道路
    "交通事故", "飲酒運転", "速度超過", "ひき逃げ", "無免許運転",
    # 不正・汚職
    "贈賄", "受賄", "汚職", "背任", "公金流用",
    # その他法律関連
    "告発", "告訴", "証人", "証拠", "警察", "捜査", "送検", "懲戒", "過失"
}

# ============================================
# 日常の意外な出来事（不思議・ミステリー・奇跡）
# ============================================
daily_surprising_keywords = {
    # 不思議・謎
    "謎", "不可解", "怪現象", "怪奇", "超自然", "幽霊", "心霊", "UFO", "宇宙人",
    "ミステリー", "不思議", "摩訶不思議", "意外", "驚き", "ビックリ",
    # 奇跡・幸運
    "奇跡", "奇跡的", "幸運", "ラッキー", "運が良い", "偶然", "九死に一生",
    # 運命・運
    "運命", "宿命", "運勢", "因縁", "呪い", "怨念",
    # 衝撃的な事実・発見
    "衝撃", "驚愕", "愕然", "仰天", "発見", "秘密", "隠していた", "判明",
    "発覚", "露見", "明かされた", "ついに判明", "真実",
    # 人間関係・ドラマ
    "恋愛", "浮気", "離婚", "親子", "兄弟", "姉妹", "夫婦", "家族関係", "相続",
    # 動物関連
    "動物", "犬", "猫", "馬", "牛", "象", "ライオン", "サメ", "クマ", "蛇",
    "野生動物", "ペット", "野性化", "襲撃",
    # 環境・自然災害
    "地震", "津波", "火山", "台風", "洪水", "暴風", "竜巻", "雪崩", "土砂崩れ",
    "自然災害", "災害", "被災", "被害",
    # その他
    "大金", "宝くじ", "一攫千金", "億万長者", "成功", "失敗", "逆転", "人生逆転",
}

# fmt: on

# ============================================
# キーワード辞書をまとめたもの
# ============================================
KEYWORD_CATEGORIES = {
    "medical": medical_keywords,
    "legal": legal_keywords,
    "daily_surprising": daily_surprising_keywords,
}

# ============================================
# ユーティリティ関数
# ============================================


def is_category(text: str, category: str) -> bool:
    """テキストが指定カテゴリのキーワードを含むかチェック"""
    if category not in KEYWORD_CATEGORIES:
        return False
    keywords = KEYWORD_CATEGORIES[category]
    return any(w in text for w in keywords)


def count_keywords_in_category(text: str, category: str) -> int:
    """テキストに含まれるカテゴリ内のキーワード出現回数をカウント"""
    if category not in KEYWORD_CATEGORIES:
        return 0
    keywords = KEYWORD_CATEGORIES[category]
    return sum(text.count(k) for k in keywords)


def classify_text(text: str) -> dict:
    """テキストを全カテゴリで分析して分類結果を返す"""
    result = {}
    for category in KEYWORD_CATEGORIES.keys():
        count = count_keywords_in_category(text, category)
        result[category] = {
            "matched": count > 0,
            "count": count,
        }
    return result


def analyze_by_keywords(df, category: str, threshold: float = 0.5) -> None:
    """
    DataFrame に時間を考慮したキーワード分析列を追加（インプレイス）

    get_youtube_data.ipynb のロジックを踏襲：
    1. 各動画のキーワード出現回数をカウント
    2. 動画時間（秒）を分に変換
    3. 1分あたりのキーワード出現回数を計算
    4. threshold 以上なら is_{category} = True

    Args:
        df: video_id, subtitles, duration(秒) を含む DataFrame（インプレイス修正）
        category: 分析カテゴリ ("medical", "legal", "daily_surprising")
        threshold: 関連性判定の閾値（デフォルト 0.5回/分）

    Example:
        >>> analyze_by_keywords(df, "medical", threshold=0.5)
        >>> # df に以下の列が追加される:
        >>> # - medical_word_count
        >>> # - duration_min
        >>> # - medical_per_min
        >>> # - is_medical
    """
    if category not in KEYWORD_CATEGORIES:
        raise ValueError(
            f"不正なカテゴリ: {category}. 有効値: {list(KEYWORD_CATEGORIES.keys())}"
        )

    # 1. キーワード出現回数
    df[f"{category}_word_count"] = df["subtitles"].apply(
        lambda t: count_keywords_in_category(str(t), category)
    )

    # 2. 動画時間を分に変換（duration は秒単位と想定）
    if "duration_min" not in df.columns:
        df["duration_min"] = df["duration"] / 60

    # 3. 1分あたりのキーワード出現回数
    df[f"{category}_per_min"] = (
        df[f"{category}_word_count"] / df["duration_min"]
    ).round(3)

    # 4. threshold 以上なら該当カテゴリとみなす
    df[f"is_{category}"] = df[f"{category}_per_min"] >= threshold


def add_title_keyword_flags(df, category: str) -> None:
    """
    タイトルに指定カテゴリのキーワードが含まれているかを判定

    Args:
        df: title カラムを含む DataFrame（インプレイス修正）
        category: カテゴリ名 ("medical", "legal", "daily_surprising")

    追加される列:
        - {category}_in_title: タイトルにキーワードが含まれるなら True

    Example:
        >>> add_title_keyword_flags(df, "medical")
        >>> # df['medical_in_title'] が追加される
    """
    if category not in KEYWORD_CATEGORIES:
        raise ValueError(f"不正なカテゴリ: {category}")

    df[f"{category}_in_title"] = (
        df["title"].fillna("").apply(lambda t: is_category(t, category))
    )
