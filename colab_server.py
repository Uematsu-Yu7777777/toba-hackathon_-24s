!pip install transformers peft flask pyngrok

from google.colab import drive
drive.mount('/content/drive')

import torch, gc
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from flask import Flask, request, jsonify
from pyngrok import ngrok
import pyngrok

pyngrok.ngrok.set_auth_token("token")


class ModelManager:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.vram_model_key = None

    def load_model(self, model_name, lora_dir=None):
        print("llama を読み込み中...")
        # ここでは常に Llama の基本モデルからトークナイザーを読み込みます
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        except TypeError as e:
            print(f"トークナイザー読み込みエラー: {e}")
            print("use_fast=Trueで再試行します")
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, low_cpu_mem_usage=True
        )
        if lora_dir:
            try:
                model = PeftModel.from_pretrained(model, lora_dir)
            except Exception as e:
                print(f"LoRA適用失敗: {e}")
        model.to("cpu")
        self.models["llama"] = model
        self.tokenizers["llama"] = tokenizer
        print("llama の読み込み完了")

    def swap_to_vram(self, key):
        if self.vram_model_key == key:
            return
        if self.vram_model_key is not None:
            self.models[self.vram_model_key].to("cpu")
            torch.cuda.empty_cache()
            gc.collect()
        self.models[key].to("cuda")
        self.vram_model_key = key

    def generate_text(self, prompt, max_new_tokens=100):
        self.swap_to_vram("llama")
        tokenizer = self.tokenizers["llama"]
        inputs = tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to("cuda") for k, v in inputs.items()}
        with torch.no_grad():
            output = self.models["llama"].generate(**inputs, max_new_tokens=max_new_tokens)
        return tokenizer.decode(output[0], skip_special_tokens=True)

app = Flask(__name__)

# ngrokでポート5000を公開
public_url = ngrok.connect(5000, bind_tls=True)
print("Public URL:", public_url)

model_manager = ModelManager()
# llamaモデルのみをロード
model_manager.load_model("elyza/Llama-3-ELYZA-JP-8B", "/content/drive/MyDrive/colab/lora")
model_manager.swap_to_vram("llama")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    target_lang = data.get("target_lang", None)  # 翻訳先の口調指定
    max_new_tokens = data.get("max_new_tokens", 100)
    
    # 翻訳先の指定に応じたシステムプロンプトの設定（例：メスガキ構文も個別に指定）
    if target_lang:
        if target_lang == "標準語":
            system_prompt = "以下の文章を、意味は変えずに標準語として正確に翻訳してください。余計な情報は一切出力せず、翻訳結果のみを出力してください。:"
        elif target_lang == "淫夢構文":
            system_prompt = "以下の文章を、意味は変えずに淫夢構文に翻訳してください。余計な情報は一切出力せず、翻訳結果のみを出力してください。:"
        elif target_lang == "メスガキ構文":
            system_prompt = "以下の文章を、意味を変えずにメスガキ構文に翻訳してください。余計な会話や解説は一切出力せず、翻訳後の文章のみを返してください。:"
        else:
            system_prompt = f"以下の文章を、意味は変えずに{target_lang}に翻訳してください。余計な情報は出力せず、翻訳結果のみを返してください。:"
        prompt = system_prompt + "\n" + prompt

    try:
        # 生成の際に温度やビームサーチのパラメータも指定して、より決定論的な出力に調整
        inputs = model_manager.tokenizers["llama"](prompt, return_tensors="pt")
        inputs = {k: v.to("cuda") for k, v in inputs.items()}
        with torch.no_grad():
            output = model_manager.models["llama"].generate(
                **inputs, 
                max_new_tokens=max_new_tokens, 
                temperature=0.0, 
                num_beams=5, 
                early_stopping=True
            )
        result = model_manager.tokenizers["llama"].decode(output[0], skip_special_tokens=True)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Flaskサーバー起動中。上記のPublic URLにアクセスしてください。")
    app.run(host="0.0.0.0", port=5000)