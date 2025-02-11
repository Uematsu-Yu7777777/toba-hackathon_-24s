import json
import os
from collections import defaultdict

# 入力ディレクトリ
DATA_DIR = "./traindata/"
# 出力ファイル
OUTPUT_FILE = "./merged_dataset.json"

def load_translation_data():
    """traindataフォルダ内のJSONファイルを読み込み、統合する"""
    dataset = defaultdict(list)

    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith(".json"):
            file_path = os.path.join(DATA_DIR, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    src_lang = data.get("source_language")
                    tgt_lang = data.get("target_language")
                    translations = data.get("translations", [])

                    if src_lang and tgt_lang and translations:
                        key = f"{src_lang}-{tgt_lang}"
                        dataset[key].extend(translations)
            except Exception as e:
                print(f"ファイル {file_name} の読み込みに失敗しました: {e}")

    return dataset

def save_merged_dataset(dataset):
    """Transformerの学習に適したフォーマットで保存"""
    formatted_data = []
    
    for key, translations in dataset.items():
        src_lang, tgt_lang = key.split("-")
        for pair in translations:
            formatted_data.append({
                "source_language": src_lang,
                "target_language": tgt_lang,
                "input_text": pair["source"],
                "target_text": pair["target"]
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    
    print(f"統合データセットが {OUTPUT_FILE} に保存されました。")

if __name__ == "__main__":
    merged_data = load_translation_data()
    save_merged_dataset(merged_data)
