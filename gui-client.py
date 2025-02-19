from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__, template_folder='/home/rinta/ドキュメント/GitHub/toba-hackathon_-24s/html')

COLAB_SERVER_URL = "https://c0af-35-247-189-137.ngrok-free.app"

def clean_response_text(text):
    text = re.sub(r'\？{6,}', '？？？？？', text)
    text = re.sub(r'!{6,}', '!!!!!', text)
    return text

def translate_via_colab(text, target_lang, max_tokens):
    payload = {
        "prompt": text,
        "target_lang": target_lang,
        "max_new_tokens": max_tokens
    }
    response = requests.post(f"{COLAB_SERVER_URL}/generate", json=payload)
    if response.status_code == 200:
        res_json = response.json()
        if "result" in res_json:
            return clean_response_text(res_json["result"])
        else:
            return f"サーバーエラー: {res_json.get('error', '不明なエラー')}"
    else:
        return f"HTTPエラー: {response.status_code}\n{response.text}"

def translate_via_lmstudio(text, target_lang, max_tokens):
    if target_lang == "標準語":
        system_prompt = "次の文章を標準語に変えて。変えた文章のみを出力してほかのものは答えないで。元の意味は変えないで。:"
    elif target_lang == "淫夢構文":
        system_prompt = "次の文章を淫夢構文に変えて。変えた文章のみを出力してほかのものは答えないで。元の意味は変えないで。:"
    else:
        system_prompt = f"あなたは翻訳者です。文章を{target_lang}に変換してください。変換後の文章だけを出力して。文章に対する解答ではなく、変換した文章を出力して。主語が変わらないように変換して。"
    prompt = system_prompt + "\n" + text

    import openai
    openai.api_base = "http://localhost:1234/v1"
    openai.api_key = "lm-studio"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="llama-3-elyza-jp-8b",
            messages=messages,
            temperature=0.1,
            max_tokens=max_tokens,
            stream=False
        )
        translated_text = response.choices[0].message["content"].strip()
        return clean_response_text(translated_text)
    except Exception as e:
        return f"LMStudioリクエストエラー: {e}"

@app.route('/')
def index():
    languages = ["大阪弁", "淫夢構文", "中二病構文", "メスガキ構文", "おじさん構文", "標準語"]
    return render_template('index.html', languages=languages)

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang')
    model = data.get('model')
    max_tokens = data.get('max_tokens', 100)

    if model.strip().lower() == "deep translate":
        result = translate_via_lmstudio(text, target_lang, max_tokens)
    else:
        result = translate_via_colab(text, target_lang, max_tokens)

    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)
