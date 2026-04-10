import requests
import json
import time
import sys
import argparse
from datetime import datetime
import os

# =========================
# 設定
# =========================
# 優先順位: 1. 環境変数 (QIITA_TOKEN) / 2. .envファイル / 3. 下記のTOKEN変数
TOKEN = "YOUR_QIITA_ACCESS_TOKEN"

def load_token():
    # 1. 環境変数をチェック
    token = os.environ.get("QIITA_TOKEN")
    if token:
        return token

    # 2. .envファイルをチェック
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("QIITA_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    # 3. コード内のTOKENをチェック
    if TOKEN != "YOUR_QIITA_ACCESS_TOKEN":
        return TOKEN

    return None

def save_token_to_env(token):
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"QIITA_TOKEN={token}\n")
    print("-> アクセストークンを .env ファイルに保存しました。次回から入力を省略できます。")

BASE_URL = "https://qiita.com/api/v2/items"

PER_PAGE = 100
MAX_PAGES = 100  # 安全上限

def main():
    parser = argparse.ArgumentParser(description='Qiitaの記事を条件指定で検索して取得します。')
    parser.add_argument('--query', type=str, help='Qiita APIのクエリ文字列 (例: "stocks:>500")')
    parser.add_argument('--year', type=str, default="2025", help='対象年 (デフォルト: 2025)')
    parser.add_argument('--stocks', type=int, default=150, help='最低ストック数 (デフォルト: 150)')
    parser.add_argument('--likes', type=int, default=0, help='最低いいね数 (デフォルト: 0)')
    parser.add_argument('--tag', type=str, help='対象タグ (例: "Python")')
    parser.add_argument('--sort', choices=['likes', 'stocks', 'created'], default='likes', help='ソート対象 (デフォルト: likes)')
    parser.add_argument('--interactive', '-i', action='store_true', help='対話形式で条件を指定する')
    
    args = parser.parse_args()

    # 引数なし、または --interactive 指定時に対話モードへ
    is_interactive = args.interactive or (not args.query and len(sys.argv) == 1)

    # トークン設定（優先順位: 環境変数 > .env > TOKEN変数 > 対話入力）
    current_token = load_token()
    
    if not current_token:
        print("Qiitaアクセストークンが設定されていません。")
        print("ヒント: トークンを入力するとAPIの利用制限が緩和されます（空欄でも実行は可能です）。")
        temp_token = input("アクセストークンを入力 (Enterでスキップ): ").strip()
        if temp_token:
            current_token = temp_token
            confirm_save = input("このトークンを .env ファイルに保存して永続化しますか？ (y/N): ").strip().lower() == "y"
            if confirm_save:
                save_token_to_env(temp_token)

    # ヘッダー設定
    headers = {}
    if current_token:
        headers["Authorization"] = f"Bearer {current_token}"
    else:
        print("警告: アクセストークンが設定されていません。APIの利用制限が適用される可能性があります。\n")

    # 対話モード
    if is_interactive:
        print("--- Qiita 記事検索設定 ---")
        use_custom_query = input("任意のクエリを直接入力しますか？ (y/N): ").strip().lower() == "y"
        
        if use_custom_query:
            args.query = input("クエリを入力してください (例: tag:python stocks:>1000): ").strip()
        else:
            tag_input = input("対象のタグを入力してください (空欄で全件対象): ").strip()
            if tag_input:
                args.tag = tag_input

            year_input = input(f"対象年を入力してください (デフォルト: {args.year}): ").strip()
            if year_input:
                args.year = year_input
            
            stocks_input = input(f"最低ストック数を入力してください (デフォルト: {args.stocks}): ").strip()
            if stocks_input:
                try:
                    args.stocks = int(stocks_input)
                except ValueError:
                    print("有効な数値を入力してください。デフォルト値を使用します。")

            likes_input = input(f"最低いいね数を入力してください (デフォルト: {args.likes}): ").strip()
            if likes_input:
                try:
                    args.likes = int(likes_input)
                except ValueError:
                    print("有効な数値を入力してください。デフォルト値を使用します。")

            print("\nソート順を選択してください:")
            print("1: いいね数 (likes)")
            print("2: ストック数 (stocks)")
            print("3: 作成日時 (created)")
            sort_choice = input("選択 (1-3, デフォルト 1): ").strip()
            if sort_choice == "2":
                args.sort = "stocks"
            elif sort_choice == "3":
                args.sort = "created"
            else:
                args.sort = "likes"

    if args.query:
        query_str = args.query
    else:
        query_parts = [
            f"created:>={args.year}-01-01",
            f"created:<={args.year}-12-31",
            f"stocks:>={args.stocks}",
            f"likes:>={args.likes}"
        ]
        if args.tag:
            query_parts.append(f"tag:{args.tag}")
        
        query_str = " ".join(query_parts)

    print(f"検索クエリ: {query_str}")
    
    items = []

    try:
        for page in range(1, MAX_PAGES + 1):
            params = {
                "page": page,
                "per_page": PER_PAGE,
                "query": query_str
            }
            print(f"Fetching page {page}...")

            r = requests.get(BASE_URL, headers=headers, params=params)
            r.raise_for_status()

            data = r.json()
            if not data:
                break

            items.extend(data)
            
            if len(data) < PER_PAGE:
                break

            time.sleep(0.2)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return

    print(f"合計 {len(items)} 件取得しました。")

    if not items:
        return

    # ソート処理
    sort_key_map = {
        'likes': 'likes_count',
        'stocks': 'stocks_count',
        'created': 'created_at'
    }
    key_field = sort_key_map[args.sort]
    items_sorted = sorted(items, key=lambda x: x.get(key_field, 0), reverse=True)

    # 整形
    result = [
        {
            "title": item["title"],
            "likes_count": item["likes_count"],
            "stocks_count": item["stocks_count"],
            "url": item["url"],
            "created_at": item["created_at"],
            "user_id": item["user"]["id"],
            "tags": [tag["name"] for tag in item.get("tags", [])]
        }
        for item in items_sorted
    ]

    # ファイル保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"qiita_search_res_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"\n完了! {output_file} に保存しました。")

if __name__ == "__main__":
    main()
import requests
import json
import time

# =========================
# 設定
# =========================
# 必要に応じてアクセストークンを記載してください
TOKEN = "YOUR_QIITA_ACCESS_TOKEN"
BASE_URL = "https://qiita.com/api/v2/items"

YEAR = "2025"
STOCKS_THRESHOLD = 150
PER_PAGE = 100
MAX_PAGES = 100  # 安全上限

OUTPUT_FILE = "qiita_2025_stocks150_sorted_by_likes_2.json"

headers = {}
if TOKEN and TOKEN != "YOUR_QIITA_ACCESS_TOKEN":
    headers["Authorization"] = f"Bearer {TOKEN}"
else:
    print("警告: アクセストークンが設定されていません。APIの利用制限が適用される可能性があります。")
    print("設定が必要な場合は、search.py の TOKEN 変数を編集してください。\n")

# =========================
# データ取得
# =========================
items = []

for page in range(1, MAX_PAGES + 1):
    params = {
        "page": page,
        "per_page": PER_PAGE,
        "query": (
            f"created:>={YEAR}-01-01 "
            f"created:<={YEAR}-12-31 "
            f"stocks:>={STOCKS_THRESHOLD}"
        )
    }
    print(f"Fetching page {page}...")

    r = requests.get(BASE_URL, headers=headers, params=params)
    r.raise_for_status()

    data = r.json()
    if not data:
        break

    items.extend(data)

    # 念のためのレート制限対策
    time.sleep(0.2)

print(f"Fetched {len(items)} items")

# =========================
# likes_count で降順ソート
# =========================
items_sorted = sorted(
    items,
    key=lambda x: x["likes_count"],
    reverse=True
)

# =========================
# 出力用に整形
# =========================
result = [
    {
        "title": item["title"],
        "likes_count": item["likes_count"],
        "stocks_count": item["stocks_count"],
        "url": item["url"],
        "created_at": item["created_at"],
        "user_id": item["user"]["id"],
    }
    for item in items_sorted
]

# =========================
# JSON 出力
# =========================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Saved {len(result)} items to {OUTPUT_FILE}")
