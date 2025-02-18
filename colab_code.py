# Google Colab用のセットアップ
from google.colab import drive
drive.mount('/content/drive')

# 必要なライブラリのインストール
!pip install -U bitsandbytes transformers peft torch flask pyngrok

# 必要なインポート
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import os
from flask import Flask, render_template, request, jsonify
import json
import re

# pyngrokのインポート
from pyngrok import ngrok

# 環境変数の設定
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# モデルとトークナイザーのパス（キャッシュディレクトリは指定しない）
model_dir = '/content/drive/MyDrive/colab/lora'

# デバイスの設定
device = "cuda" if torch.cuda.is_available() else "cpu"

# 以下、不要な "float16" 行を削除しました
# float16

# ベースモデルをロード
base_model = AutoModelForCausalLM.from_pretrained("elyza/Llama-3-ELYZA-JP-8B", torch_dtype=torch.float16).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_dir)

# LoRA アダプターを適用
fine_tuned_model = PeftModel.from_pretrained(base_model, model_dir).to(device)

# 追加: deep translate用モデルのロード（初期はRAM上に置く）
deep_model = AutoModelForCausalLM.from_pretrained(
    "cyberagent/DeepSeek-R1-Distill-Qwen-14B-Japanese",
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True
)
deep_tokenizer = AutoTokenizer.from_pretrained("cyberagent/DeepSeek-R1-Distill-Qwen-14B-Japanese")

# 追加: モデルを指定のデバイスに移動するためのヘルパー関数
def move_model(model, target_device):
    if next(model.parameters()).device.type != target_device:
        model.to(target_device)

# Flaskアプリケーションの設定
app = Flask(__name__, static_folder='/content/drive/MyDrive/colab/html', template_folder='/content/drive/MyDrive/colab/html')

# 利用可能な言語リスト
LANGUAGES = {
    "自然な大阪弁": "大阪弁",
    "淫夢語録の言葉を多用するようような文章": "淫夢構文",
    "中二病言葉を多用するようような文章": "中二病構文",
    "メスガキ構文": "メスガキ",
    "絵文字を多用するおじさん構文": "おじさん",
    "標準語": "標準語"
}

# 淫夢構文の翻訳データを読み込む
with open('/content/drive/MyDrive/colab/translation_標準語_to_淫夢構文.json', 'r', encoding='utf-8') as file:
    inmu_translations = json.load(file)["translations"]

@app.route("/")
def index():
    return render_template("index.html", languages=LANGUAGES)

@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text")
    target_lang = data.get("target_lang")
    selected_model = data.get("model")  # "llama-3-elyza-jp-8b" または "cyberagent-deepseek-r1-distill-qwen-14b-japanese"

    if not text or target_lang not in LANGUAGES:
        return jsonify({"error": "Invalid input"}), 400

    if target_lang == "標準語":
        system_prompt = "次の文章を標準語に変えて。変えた文章のみを出力してほかのものは答えないで。元の文から意味は変えないで。:"
    elif target_lang == "淫夢構文":
        inmu_phrases = "\n".join([f"{t['source']} -> {t['target']}" for t in inmu_translations])
        system_prompt = f"次の文章を淫夢構文に変えて。変えた文章のみを出力してほかのものは答えないで。元の文から意味は変えないで。\n\n淫夢語録:\n{inmu_phrases}\n\n文章:"
    else:
        system_prompt = f"あなたは文章の口調変換エキスパートです。次の文章を {target_lang} に変換してください。変換後の文章のみを出力し、他の情報は一切出力に含めないでください。大きく言っている意味を変えないでください。:"

    # 追加: 選択されたモデルに応じた処理（deep translateの場合はGPUとRAM間を入れ替え）
    if selected_model == "cyberagent-deepseek-r1-distill-qwen-14b-japanese":
        move_model(deep_model, device)
        move_model(fine_tuned_model, "cpu")
        current_tokenizer = deep_tokenizer
        current_model = deep_model
    else:
        move_model(fine_tuned_model, device)
        move_model(deep_model, "cpu")
        current_tokenizer = tokenizer
        current_model = fine_tuned_model

    # プロンプト結合
    prompt = system_prompt + "\n" + text

    inputs = current_tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        output = current_model.generate(**inputs, max_new_tokens=50, num_beams=5, early_stopping=True)
    translated_text = current_tokenizer.decode(output[0], skip_special_tokens=True)
    translated_text = re.sub(r'<think>.*?</think>', '', translated_text)
    return jsonify({"translated_text": translated_text})

# Ngrokトンネルの起動
public_url = ngrok.connect(5000)
print("Public URL:", public_url)

if __name__ == "__main__":
    app.run(use_reloader=False)