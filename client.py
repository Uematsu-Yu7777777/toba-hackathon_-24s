import requests
import json
import re

# ※ 下記URLを、Colabサーバー起動時に表示されたngrokのURLに置き換えてください
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
    print("Colabサーバーにリクエスト中...")
    response = requests.post(f"{COLAB_SERVER_URL}/generate", json=payload)
    if response.status_code == 200:
        res_json = response.json()
        if "result" in res_json:
            cleaned_result = clean_response_text(res_json["result"])
            print("\n【翻訳結果 (llama)】")
            print(cleaned_result)
        else:
            print("サーバーエラー:", res_json.get("error", "不明なエラー"))
    else:
        print("HTTPエラー:", response.status_code)
        print(response.text)

def translate_via_lmstudio(text, target_lang, max_tokens):
    # LMStudio 用のシステムプロンプトを組み立てる
    if target_lang == "標準語":
        system_prompt = "次の文章を標準語に変えて。変えた文章のみを出力してほかのものは答えないで。元の意味は変えないで。:"
    elif target_lang == "淫夢構文":
        # ※ 必要に応じて翻訳データを組み込むか、固定メッセージにしてください。
        system_prompt = "次の文章を淫夢構文に変えて。変えた文章のみを出力してほかのものは答えないで。元の意味は変えないで。:"
    elif target_lang == "大阪弁":
        system_prompt = "次の文章を大阪弁に変換してください。変換後の文章だけを出力して。濃くない大阪弁にして。標準語に近づけて。:"
    else:
        system_prompt = f"次の文章を{target_lang}に変換してください。変換後の文章だけを出力して。:"
    prompt = system_prompt + "\n" + text

    # LMStudio は OpenAI API 互換となっているため、openai パッケージを利用します
    import openai
    openai.api_base = "http://localhost:1234/v1"
    openai.api_key = "lm-studio"  # 適宜変更してください

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    print("LMStudioにリクエスト中...")
    try:
        response = openai.ChatCompletion.create(
            model="cyberagent-deepseek-r1-distill-qwen-14b-japanese",  # LMStudio側の deepseek モデルを指定
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
            stream=False
        )
        translated_text = response.choices[0].message["content"].strip()
        cleaned_translated_text = clean_response_text(translated_text)
        print("\n【翻訳結果 (deepseek)】")
        print(cleaned_translated_text)
    except Exception as e:
        print("LMStudioリクエストエラー:", e)

def main():
    print("翻訳クライアント　-　ColabサーバーまたはLMStudioと通信します")
    print("※ 対応の翻訳先例：標準語、淫夢構文、自然な大阪弁　など")
    text = input("翻訳する文章を入力してください: ")
    target_lang = input("翻訳先（口調）を入力してください: ")
    model = input("使用するモデルを指定してください (llama / deepseek): ")
    max_tokens_input = input("生成する最大トークン数 (数字) [100]: ")

    try:
        max_tokens = int(max_tokens_input)
    except:
        max_tokens = 100

    if model.strip().lower() == "deepseek":
        translate_via_lmstudio(text, target_lang, max_tokens)
    else:
        translate_via_colab(text, target_lang, max_tokens)

if __name__ == "__main__":
    main()