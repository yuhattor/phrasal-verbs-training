import os
from openai import OpenAI
import re
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

# OpenAI クライアントの初期化（環境変数から API キーを取得）
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def clean_text(text):
    # Markdownの強調記号(**) を削除
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    return text.strip()

def is_valid_sentence(text):
    # 空のテキストをスキップ
    if not text.strip():
        return False
    
    # コメントブロックをスキップ
    if text.strip().startswith('<!--') or text.strip().endswith('-->'):
        return False
    
    # Markdownの見出しをスキップ
    if text.strip().startswith('#'):
        return False
    
    # 箇条書きをスキップ
    if text.strip().startswith('-'):
        return False
    
    # 少なくとも1つの有効な文字を含むことを確認
    if not any(c.isalnum() for c in text):
        return False
    
    return True

def update_talk_file(talk_file, original_text, audio_path):
    try:
        # ファイルの内容を読み込む
        with open(talk_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # 元のテキストを探し、その後にaudioタグを挿入
        # 既存のaudioタグがある場合は置き換えない
        search_text = re.escape(original_text.strip())
        audio_tag = f'\n<audio controls src="{audio_path}"></audio>\n'
        
        # テキストの後に既にaudioタグがあるかチェック
        if not re.search(f'{search_text}\s*<audio.*?</audio>', content, re.DOTALL):
            # audioタグがない場合は追加
            content = re.sub(
                f'({search_text})',
                f'\\1{audio_tag}',
                content
            )

            # 更新した内容を書き込む
            with open(talk_file, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Updated {talk_file} with audio tag")
        else:
            print(f"Audio tag already exists for the text in {talk_file}")

    except Exception as e:
        print(f"Error updating {talk_file}: {str(e)}")

def process_markdown_file(input_file, output_dir, file_number, split_chunks=True):
    # Markdownファイルを読み込む
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()
    
    if split_chunks:
        # 空行2つで分割
        chunks = content.split('\n\n')
        # 有効なチャンクを抽出
        valid_chunks = [clean_text(chunk) for chunk in chunks if is_valid_sentence(chunk)]

        # 対応するtalkファイルのパス
        talk_file = os.path.join("LearningEnglish", f"talk-{file_number}.md")

        # 各チャンクを音声に変換
        for i, chunk in enumerate(valid_chunks, 1):
            if chunk:  # 空でないチャンクのみ処理
                output_file = f"{output_dir}/sentence-{i:03d}.mp3"
                
                # Text-to-Speech APIを呼び出し
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="echo",
                    input=chunk
                )
                
                # 音声ファイルを保存
                response.stream_to_file(output_file)
                print(f"Generated: {output_file}")

                # talkファイルを更新
                relative_path = os.path.relpath(output_file, os.path.dirname(talk_file))
                update_talk_file(talk_file, chunk, relative_path)
    else:
        # ファイル全体を1つの音声として処理
        cleaned_content = clean_text(content)
        if is_valid_sentence(cleaned_content):
            output_file = f"{output_dir}/full-audio.mp3"
            
            # Text-to-Speech APIを呼び出し
            response = client.audio.speech.create(
                model="tts-1",
                voice="echo",
                input=cleaned_content
            )
            
            # 音声ファイルを保存
            response.stream_to_file(output_file)
            print(f"Generated: {output_file}")

            # talkファイルを更新
            talk_file = os.path.join("LearningEnglish", f"talk-{file_number}.md")
            relative_path = os.path.relpath(output_file, os.path.dirname(talk_file))
            update_talk_file(talk_file, cleaned_content, relative_path)

def main(split_chunks=True):
    # 処理対象のファイル
    base_dir = "LearningEnglish"
    files = [f"forvoice-{i}.md" for i in range(1, 6)]

    for i, filename in enumerate(files, 1):
        input_file = os.path.join(base_dir, filename)
        output_dir = f"output/conversation-{i}"
        
        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nProcessing {filename}...")
        process_markdown_file(input_file, output_dir, i, split_chunks)
        print(f"Completed processing {filename}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-split', action='store_true', help='Generate a single audio file instead of splitting')
    args = parser.parse_args()
    
    main(split_chunks=not args.no_split)
