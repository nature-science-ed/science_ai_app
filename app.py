import streamlit as st
import pandas as pd
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from openai import OpenAI

# --- 1. ページ設定 ---
st.set_page_config(page_title="AI Reflection Analyzer", layout="wide")
st.title("🔬 AIリフレクション・アナライザー")

# --- 2. API設定 (Secrets) ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("APIキーが設定されていません。Streamlit CloudのSecretsを確認してください。")
    st.stop()

# --- 3. サイドバー設定 ---
st.sidebar.header("📋 行事のねらい設定")
goal_1 = st.sidebar.text_area("ねらい1", "最先端の科学研究に触れ、興味・関心を高める。")
goal_2 = st.sidebar.text_area("ねらい2", "大学での学びを知り、将来の進路について考えるきっかけとする。")

t = Tokenizer()

# --- 4. 単語抽出エンジンの改良 ---
def extract_words(text):
    words = []
    # 感情語リスト
    feeling_words = ["思う", "感じる", "考える", "知る", "驚く", "わかる", "面白い", "楽しい", "凄い", "すごい", "不思議"]
    
    if not text or pd.isna(text):
        return ""

    for token in t.tokenize(str(text)):
        part = token.part_of_speech.split(",")[0]
        base = token.base_form
        
        # 名詞（1文字以上でも可にする）または特定の感情語
        if part == "名詞" or base in feeling_words:
            # 1文字の一般的な名詞（こと、もの等）を避けるための最小限の除外
            if base not in ["こと", "もの", "よう", "そう", "これ", "それ"]:
                words.append(base)
    
    return " ".join(words)

# --- 5. メイン処理 ---
uploaded_file = st.file_uploader("エクセルまたはCSVファイルをアップロードしてください", type=["xlsx", "csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    target_col = st.selectbox("分析したい感想の列を選択してください", df.columns)
    
    if st.button("AI詳細分析を実行"):
        all_text = "\n".join(df[target_col].dropna().astype(str))
        wakati = extract_words(all_text)
        
        # ★重要：単語がゼロの場合のチェック
        if not wakati.strip():
            st.error("テキストから単語を抽出できませんでした。列の選択が正しいか、データに日本語の感想が含まれているか確認してください。")
        else:
            with st.spinner("AIが分析中..."):
                # ワードクラウド作成
                # フォントパスはインストールされた fonts-noto-cjk を参照
                FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
                
                try:
                    wc = WordCloud(font_path=FONT_PATH, background_color="white", width=1000, height=500).generate(wakati)
                    
                    img_buf = io.BytesIO()
                    wc.to_image().save(img_buf, format='PNG')
                    img_bytes = img_buf.getvalue()
                    
                    st.image(img_bytes)

                    # AI評価 (GPT-4o)
                    base64_image = base64.b64encode(img_bytes).decode('utf-8')
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"このワードクラウド画像を分析し、次のねらいへの達成度を評価して下さい。1:{goal_1} 2:{goal_2}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                            ]
                        }]
                    )
                    st.divider()
                    st.header("📝 AI評価レポート")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
