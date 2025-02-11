from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# LMstudio API 接続
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# 利用可能な言語リスト（追加・管理が簡単）
LANGUAGES = {
    "関西弁": "関西弁",
    "東北": "東北弁",
    "京都": "京都弁",
    "メスガキ構文": "メスガキ",
    "おじさん構文": "おじさん",
    "標準語": "標準語"
}

@app.route("/")
def index():
    return render_template("index.html", languages=LANGUAGES)

@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text")
    target_lang = data.get("target_lang")

    if not text or target_lang not in LANGUAGES:
        return jsonify({"error": "Invalid input"}), 400

    # LMstudio へリクエスト送信
    if target_lang == "原文":
        system_prompt = "次の文章を標準語に変えて。変えた文章のみを出力してほかのものは答えないで。元の文から意味は変えないで。:"
    else:
        system_prompt = f"次の文章を {LANGUAGES[target_lang]}に変えて。変えた文章のみを出力してほかのものは答えないで。元の文から意味は変えないで。:"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    completion = client.chat.completions.create(
        model="model-identifier",
        messages=messages,
        temperature=0.7,
        stream=False,
    )

    translated_text = completion.choices[0].message.content.strip()

    return jsonify({"translated_text": translated_text})

if __name__ == "__main__":
    app.run(debug=True)
