import streamlit as st
import pandas as pd
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from openai import OpenAI

# 1. ページ設定
st.set_page_config(page_title="AI Reflection Analyzer", layout="wide")
st.title("🔬 AIリフレクション・アナライザー")

# 2. OpenAI API設定 (Secretsから取得)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("APIキーが設定されていません。Streamlit CloudのSettings > Secretsを確認してください。")
    st.stop()

# 3. サイドバー：ねらいの設定（ここで入力欄が出ます）
st.sidebar.header("📋 行事のねらい設定")
goal_1 = st.sidebar.text_area("ねらい1", "地域（邑南町）の魅力や課題について理解を深める。")
goal_2 = st.sidebar.text_area("ねらい2", "農業や特産品（柚子胡椒等）を通じた地域活性化について考える。")

t = Tokenizer()

# 4. 単語抽出エンジン
def extract_words(text):
    words = []
    feel = ["思う", "感じる", "考える", "知る", "驚く", "わかる", "面白い", "楽しい", "凄い", "すごい", "不思議"]
    if not text or pd.isna(text):
        return ""
    for token in t.tokenize(str(text)):
        part = token.part_of_speech.split(",")[0]
        base = token.base_form
        if (part == "名詞" and len(base) >= 2) or (base in feel):
            if base not in ["こと", "もの", "よう", "そう"]:
                words.append(base)
    return " ".join(words)

# 5. メイン処理
uploaded_file = st.file_uploader("エクセルまたはCSVファイルをアップロードしてください", type=["xlsx", "csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    target_col = st.selectbox("分析したい感想の列を選択してください", df.columns)
    
    if st.button("AIによる分析と詳細評価を実行"):
        with st.spinner("AIが画像と文章を分析しています..."):
            all_text = "\n".join(df[target_col].dropna().astype(str))
            wakati = extract_words(all_text)
            
            if not wakati.strip():
                st.warning("単語が抽出できませんでした。列の選択を確認してください。")
            else:
                # ワードクラウド作成
                FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
                wc = WordCloud(font_path=FONT_PATH, background_color="white", width=1000, height=500).generate(wakati)
                
                img_buf = io.BytesIO()
                wc.to_image().save(img_buf, format='PNG')
                img_bytes = img_buf.getvalue()
                
                # 画像表示
                st.subheader("📊 分析結果：ワードクラウド")
                st.image(img_bytes)

                # OpenAI (GPT-4o) による画像分析
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"中学校教師としてこの画像を分析し、ねらいへの達成度を評価して。ねらい1:{goal_1} ねらい2:{goal_2}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]
                    }]
                )
                
                st.divider()
                st.header("📝 AI評価レポート")
                st.markdown(response.choices[0].message.content)
                st.download_button("画像を保存", data=img_bytes, file_name="analysis.png")
