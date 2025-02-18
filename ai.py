from flask import Flask, render_template, request, jsonify
import openai
import json
import re

app = Flask(__name__)

# LMstudio API 接続
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"

# 利用可能な言語リスト（追加・管理が簡単）
LANGUAGES = {
    "自然な大阪弁": "大阪弁",
    "淫夢語録の言葉を多用するようような文章": "淫夢構文",
    "中二病言葉を多用するようような文章": "中二病構文",
    "メスガキ構文": "メスガキ",
    "絵文字を多用するおじさん構文": "おじさん",
    "標準語": "標準語"
}

# 淫夢構文の翻訳データを読み込む
with open(r'E:\MESUGAKI-koubun\traindata\translation_標準語_to_淫夢構文.json', 'r', encoding='utf-8') as file:
    inmu_translations = json.load(file)["translations"]

@app.route("/")
def index():
    return render_template("index.html", languages=LANGUAGES)

@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text")
    target_lang = data.get("target_lang")
    model = data.get("model")

    if not text or target_lang not in LANGUAGES:
        return jsonify({"error": "Invalid input"}), 400

    if target_lang == "標準語":
        system_prompt = "次の文章を標準語に変えて。変えた文章のみを出力してほかのものは答えないで。元の文から意味は変えないで。:"
    elif target_lang == "淫夢構文":
        # 淫夢構文の翻訳を行う
        inmu_phrases = "\n".join([f"{t['source']} -> {t['target']}" for t in inmu_translations])
        system_prompt = f"次の文章を淫夢構文に変えて。変えた文章のみを出力してほかのものは答えないで。元の文から意味は変えないで。\n\n淫夢語録:\n{inmu_phrases}\n\n文章:"
    else:
        system_prompt = f"あなたは文章の口調変換エキスパートです。次の文章を {target_lang} に変換してください。変換後の文章のみを出力し、他の情報は一切出力に含めないでください。大きく言っている意味を変えないでください。:"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,
        stream=False,
    )

    translated_text = response.choices[0].message["content"].strip()

    # Remove text enclosed in <think></think> tags
    translated_text = re.sub(r'<think>.*?</think>', '', translated_text)

    return jsonify({"translated_text": translated_text})

if __name__ == "__main__":
    app.run(debug=True)