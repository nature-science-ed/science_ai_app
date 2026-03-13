import streamlit as st
import pandas as pd
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from openai import OpenAI

st.set_page_config(page_title="AI Reflection Analyzer", layout="wide")
st.title("🔬 AIリフレクション・アナライザー")

# API設定
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("SecretsにAPIキーが見つかりません。")
    st.stop()

# サイドバー
goal_1 = st.sidebar.text_area("ねらい1", "最先端の科学研究に触れ、興味・関心を高める。")
goal_2 = st.sidebar.text_area("ねらい2", "大学での学びを知り、将来の進路について考えるきっかけとする。")

t = Tokenizer()

def extract_words(text):
    words = []
    feel = ["思う", "感じる", "考える", "知る", "驚く", "わかる", "面白い", "楽しい", "凄い", "不思議"]
    for token in t.tokenize(str(text)):
        part = token.part_of_speech.split(",")[0]
        base = token.base_form
        if (part == "名詞" and len(base) >= 2) or (base in feel):
            words.append(base)
    return " ".join(words)

uploaded_file = st.file_uploader("エクセル/CSVをアップロード", type=["xlsx", "csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    target_col = st.selectbox("分析列を選択", df.columns)
    
    if st.button("AI詳細分析を実行"):
        with st.spinner("AIが画像とテキストを分析中..."):
            all_text = "\n".join(df[target_col].dropna().astype(str))
            wakati = extract_words(all_text)
            
            # 画像作成
            FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
            wc = WordCloud(font_path=FONT_PATH, background_color="white", width=1000, height=500).generate(wakati)
            img_buf = io.BytesIO()
            wc.to_image().save(img_buf, format='PNG')
            img_bytes = img_buf.getvalue()
            
            # 画像表示
            st.image(img_bytes)

            # AI評価
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": f"このワードクラウド画像を中学校教師の視点で分析し、次の『ねらい』への達成度を評価して下さい。1:{goal_1} 2:{goal_2}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}]
            )
            st.write("---")
            st.header("📝 AI評価レポート")
            st.markdown(response.choices[0].message.content)
