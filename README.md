# Qiita Data Toolkit

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Qiita API](https://img.shields.io/badge/Qiita%20API-v2-active)
![Libraries](https://img.shields.io/badge/dependencies-3-blue)
![Repo Size](https://img.shields.io/github/repo-size/shiro-shihi/Qiita-Data-Toolkit)
![Last Commit](https://img.shields.io/github/last-commit/shiro-shihi/Qiita-Data-Toolkit)

Qiita ユーザーの記事取得・検索・分析・可視化を行う CLI ツール群です。

[English README is here](README_en.md)

本プロジェクトは個人の開発・分析用途で作成したものです。必要に応じて Fork やコードの改変を行っていただいて構いませんが、利用にあたっては [MIT License](LICENSE.md) に基づき、著作権表示およびライセンス表示を維持してください。

## 想定ユースケース

- 人気記事の傾向分析
- 技術タグごとのトレンド調査
- Qiita投稿戦略の分析
- データ分析の練習素材として利用

## プロジェクト構成

```text
.
├── analyze.py        # 取得済みデータの集計・グラフ化
├── search.py         # 条件を指定した記事検索と取得
├── users.py          # 特定ユーザーの記事一覧取得
├── requirements.txt  # 依存ライブラリ一覧
├── LICENSE.md        # MIT ライセンス詳細
└── README.md         # 本ファイル
```

## セットアップ

### 1. 依存ライブラリのインストール

`requirements.txt` からまとめてインストールできます。

```bash
pip install -r requirements.txt
```

個別に入れる場合は以下です。

```bash
pip install requests pandas matplotlib
```

### 2. アクセストークンの設定（推奨）

Qiita API の利用制限を回避するために、アクセストークンの設定を推奨します。

- **自動設定（おすすめ）**: 各スクリプトをそのまま実行してください。トークンが未設定の場合、入力を促すプロンプトが表示されます。そこで入力し「保存」を選択すると、`.env` ファイルが自動生成され、次回から入力が不要になります。
- **環境変数**: システムの環境変数 `QIITA_TOKEN` にトークンを設定しても動作します。
- **手動設定**: `.env` ファイルを自分で作成し、以下のように記述することでも設定可能です。

  ```text
  QIITA_TOKEN=あなたのアクセストークン
  ```

> [!NOTE]
> 本プロジェクトでは、初心者の導入ハードルを下げるため、あえて `python-dotenv` などの外部ライブラリを使用せず、標準機能のみで `.env` の読み込みや自動生成を行っています。これにより、追加のインストールなしですぐに使い始めることができます。

## 使い方

### ユーザーの記事取得

[users.py](users.py) を実行し、Qiita ユーザー ID を指定してください。

```bash
# 対話形式で設定 (引数なし)
python users.py

# オプション指定で直接実行 (例: ユーザー 'qiita', いいね50以上)
python users.py qiita --likes 50 --sort 1
```

### 検索条件を指定して取得

[search.py](search.py) を使用し、対象年や最低ストック数などの条件を指定して取得します。

```bash
# 対話形式で条件を設定 (引数なし)
python search.py

# オプション指定で直接実行 (例: 2024年, ストック数500以上, いいね数100以上, タグ Python)
python search.py --year 2024 --stocks 500 --likes 100 --tag Python

# 任意のクエリを指定 (例: pythonタグが付いた累計ストック1000以上の記事)
python search.py --query "tag:python stocks:>1000"

# ソート順の指定 (likes/stocks/created)
python search.py --sort stocks
```

### 取得データを分析・可視化

[analyze.py](analyze.py) を使用し、取得した JSON ファイルを分析・可視化（グラフ化）できます。

```bash
# 対話形式でファイルを選択して実行 (推奨)
python analyze.py

# 特定のファイルを直接指定して実行
python analyze.py qiita_search_res_20260410_120000.json

# 出力先ディレクトリや集計件数を指定
python analyze.py data.json --out-dir my_report --top-tags 20
```

主な出力ファイル:

- `analysis_output/articles_sorted_by_likes.csv`
- `analysis_output/summary.csv`
- `analysis_output/likes_distribution.png`
- `analysis_output/stocks_distribution.png`
- `analysis_output/top_tags.png`
- `analysis_output/monthly_trend.png`

## 注意事項

- 本ツールは [Qiita API v2](https://qiita.com/api/v2/docs) を使用しています。利用にあたっては [Qiita利用規約](https://qiita.com/terms) を遵守してください。
- API の利用制限（レートリミット）に注意して実行してください。
- 本ツールに関するお問い合わせは [info@shihiro.com](mailto:info@shihiro.com) までお願いいたします。
- Qiita株式会社より削除の申し立てがあった場合は、即時に公開を停止または削除いたします。

## 開発・貢献

もし改善案や新機能のアイデアがあれば、ぜひ Pull Request を送ってください！バグ報告も歓迎です。

## ライセンス

本プロジェクトは [MIT License](LICENSE.md) のもとで公開されています。

また、本プロジェクトで使用している主要なライブラリのライセンスは以下の通りです。

- [requests](https://github.com/psf/requests) (Apache License 2.0)
- [pandas](https://github.com/pandas-dev/pandas) (BSD 3-Clause License)
- [matplotlib](https://github.com/matplotlib/matplotlib) (Matplotlib License)

Copyright (c) 2026 shihiro.com
