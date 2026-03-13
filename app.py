import streamlit as st
from openai import OpenAI

# --- API設定 (Streamlit CloudのSecretsを使用) ---
# Web公開時は.envではなくSecretsを使うのが最も確実で安全です
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("APIキーが設定されていません。Streamlit CloudのSettings > Secretsを確認してください。")
    st.stop()

st.title("思考力アシスタント")
st.write("記述式の答えに対して助言を返して、正しい考え方に近づけるアプリです。")

question = st.text_area("質問（記述式）を入力してください")
student_answer = st.text_area("回答を入力してください")

if st.button("アドバイスをもらう"):
    if not question or not student_answer:
        st.warning("質問と回答の両方を入力してください。")
    else:
        with st.spinner("AIが回答を分析しています..."):
            prompt = f"""
あなたは中学生向け理科の指導アシスタントです。
以下の問題文と生徒の解答を読み，解答の質を次の3つのどれかに分類して下さい。

S: 中学生レベルとして十分に正しく、その中でも特に優れている。
A: 中学生レベルとして十分に正しい。
B: 大筋はよいが，説明があいまい／一部が抜けている。
C: 重要な部分で誤解や間違いがある。

【問題】
{question}

【生徒の考え】
{student_answer}

### 出力ルール
1. 1行目で必ず「判定：S」「判定：A」「判定：B」「判定：C」のどれかを書く。

2. 2行目以降で助言を書く。
   - 判定Sのとき：
     - 中学生レベルとして十分に良いことをはっきり伝える。
     - 良い点を1〜2個ほめる。
     - 必要なら1〜2文だけ簡単な補足，さらに考えるための一言を添える。

   - 判定Aのとき：
     - 中学生レベルとして十分に良いことをはっきり伝える。
     - 良い点を1〜2個ほめる。
     - 必要なら1〜2文だけ簡単な補足，さらに考えるための一言を添える。

   - 判定BまたはCのとき：
     - まず良い点を1つ以上ほめる。
     - どこを直すとよくなるかを，中学生にも分かる言葉でやさしく伝える。
     - 次の一歩として，何を考えたり調べたりするとよいかの1〜3個提案する。

3. 正解そのものは直接書かない。
4. 文章はすべて日本語で，中学生にも読みやすい表現にする。
"""

            # 以前のコードの client.responses.create は古い形式のため、最新の形式に修正しました
            response = client.chat.completions.create(
                model="gpt-4o-mini", # 以前のgpt-4.1-miniは存在しないため、高速で賢い4o-miniに設定しています
                messages=[
                    {"role": "system", "content": "あなたは親切な理科の先生です。"},
                    {"role": "user", "content": prompt}
                ]
            )
            ai_message = response.choices[0].message.content

            st.subheader("アドバイス：")
            st.write(ai_message)
