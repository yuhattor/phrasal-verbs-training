# Text-to-Speech Converter for English Learning Materials

OpenAIのText-to-Speech APIを使用して、英語学習用のマークダウンファイルから音声ファイルを生成するスクリプトです。

## セットアップ

1. 必要な依存関係をインストール:
```bash
pip install openai
```

2. OpenAI APIキーを設定:
- OpenAIのアカウントを作成し、APIキーを取得
- スクリプト内の 

api_key

 を自分のキーに置き換え

## 使用方法

### 基本的な実行方法:
```bash
python scripts/text-to-speech.py
```
- 各マークダウンファイルを段落ごとに分割して音声ファイルを生成します
- 生成された音声ファイルは `output/conversation-X/` ディレクトリに保存されます

### 単一の音声ファイルとして生成:

```bash
python scripts/text-to-speech.py --no-split
```
- 各マークダウンファイルを1つの音声ファイルとして生成します

## ファイル構造

```
.
├── LearningEnglish/
│   ├── forvoice-1.md
│   ├── forvoice-2.md
│   └── ...
├── output/
│   ├── conversation-1/
│   ├── conversation-2/
│   └── ...
└── scripts/
    └── text-to-speech.py
```

## 注意事項

- マークダウンファイルは 

LearningEnglish

 ディレクトリに配置してください
- 音声は自動的に 

output

 ディレクトリ内の対応するフォルダに生成されます