import json

def create_translation_dataset():
    # 言語設定
    src_lang = input("元の言語を入力してください: ")
    tgt_lang = input("翻訳後の言語を入力してください: ")
    
    dataset = {
        "source_language": src_lang,
        "target_language": tgt_lang,
        "translations": []
    }
    
    print("翻訳ペアを入力してください。終了するには 'exit' を入力してください。")
    
    while True:
        source_text = input(f"{src_lang}のテキスト: ")
        if source_text.lower() == "exit":
            break
        
        target_text = input(f"{tgt_lang}の翻訳: ")
        if target_text.lower() == "exit":
            break
        
        dataset["translations"].append({
            "source": source_text,
            "target": target_text
        })
    
    # JSONファイルに保存
    file_name = f"translation_{src_lang}_to_{tgt_lang}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
    
    print(f"データセットが {file_name} に保存されました。")

if __name__ == "__main__":
    create_translation_dataset()
