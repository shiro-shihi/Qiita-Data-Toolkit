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

PER_PAGE = 100

def fetch_user_items(user_id, min_likes=0, min_stocks=0, target_tag=None, token=None):
    base_url = f"https://qiita.com/api/v2/users/{user_id}/items"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        print("警告: アクセストークンが設定されていません。APIの利用制限が適用される可能性があります。\n")

    all_items = []
    page = 1

    print(f"ユーザー '{user_id}' の記事を取得中...")

    while True:
        params = {
            "page": page,
            "per_page": PER_PAGE
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 404:
            print(f"エラー: ユーザー '{user_id}' が見つかりませんでした。")
            return None
        
        response.raise_for_status()
        
        data = response.json()
        if not data:
            break
            
        # 必要な情報のみに絞り込む（本文 body を除外）
        for item in data:
            # フィルタリング
            likes = item.get("likes_count", 0)
            stocks = item.get("stocks_count", 0)
            tags = [tag.get("name") for tag in item.get("tags", [])]

            if likes < min_likes:
                continue
            if stocks < min_stocks:
                continue
            if target_tag and target_tag not in tags:
                continue

            simplified_item = {
                "id": item.get("id"),
                "title": item.get("title"),
                "url": item.get("url"),
                "likes_count": likes,
                "stocks_count": stocks,
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "tags": tags
            }
            all_items.append(simplified_item)

        print(f"Page {page}: {len(data)}件取得 (条件一致: {len(all_items)}件)")
        
        # ページネーションの終了判定
        if len(data) < PER_PAGE:
            break
            
        page += 1
        time.sleep(0.2) # レート制限対策

    return all_items

def sort_items(items, sort_choice=None):
    if not sort_choice:
        print("\nソート順を選択してください:")
        print("1: いいね数（多い順）")
        print("2: いいね数（少ない順）")
        print("3: 投稿日（新しい順）")
        print("4: 投稿日（古い順）")
        
        sort_choice = input("選択 (1-4): ").strip()

    if sort_choice == "1":
        items.sort(key=lambda x: x.get("likes_count", 0), reverse=True)
        print("-> いいね数（多い順）にソートしました。")
    elif sort_choice == "2":
        items.sort(key=lambda x: x.get("likes_count", 0))
        print("-> いいね数（少ない順）にソートしました。")
    elif sort_choice == "3":
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        print("-> 投稿日（新しい順）にソートしました。")
    elif sort_choice == "4":
        items.sort(key=lambda x: x.get("created_at", ""))
        print("-> 投稿日（古い順）にソートしました。")
    else:
        print("-> デフォルト順で保存します。")
    
    return items

def main():
    parser = argparse.ArgumentParser(description='Qiitaユーザーの記事を取得してJSONで保存します。')
    parser.add_argument('user_id', nargs='?', help='Qiitaユーザーネーム')
    parser.add_argument('--likes', type=int, default=0, help='最低いいね数 (デフォルト: 0)')
    parser.add_argument('--stocks', type=int, default=0, help='最低ストック数 (デフォルト: 0)')
    parser.add_argument('--tag', type=str, help='対象タグ')
    parser.add_argument('--sort', choices=['1', '2', '3', '4'], help='ソート順 (1:いいね降順, 2:いいね昇順, 3:日付降順, 4:日付昇順)')
    
    args = parser.parse_args()

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

    # 対話モードの判定 (ユーザーIDが未指定の場合)
    if not args.user_id:
        print("--- Qiita ユーザー記事取得設定 ---")
        user_id = input("取得したいQiitaユーザーネームを入力してください: ").strip()
        if not user_id:
            print("ユーザーネームを入力してください。")
            return
        
        tag_input = input("対象のタグを入力してください (空欄で全件対象): ").strip()
        if tag_input:
            args.tag = tag_input

        likes_input = input(f"最低いいね数を入力してください (デフォルト: {args.likes}): ").strip()
        if likes_input:
            try:
                args.likes = int(likes_input)
            except ValueError: pass

        stocks_input = input(f"最低ストック数を入力してください (デフォルト: {args.stocks}): ").strip()
        if stocks_input:
            try:
                args.stocks = int(stocks_input)
            except ValueError: pass
    else:
        user_id = args.user_id

    try:
        items = fetch_user_items(user_id, min_likes=args.likes, min_stocks=args.stocks, target_tag=args.tag, token=current_token)
        if items:
            items = sort_items(items, sort_choice=args.sort)
            # ファイル名に日時を追加 (YYYYMMDD_HHMMSS)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"qiita_items_{user_id}_{timestamp}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=4)
            print(f"\n完了! {len(items)}件の記事を {output_file} に保存しました。")
        elif items is not None:
            print("条件に一致する記事が見つかりませんでした。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
