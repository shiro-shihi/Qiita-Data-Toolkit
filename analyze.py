import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# 日本語表示の設定
plt.rcParams["font.family"] = "MS Gothic" if sys.platform == "win32" else "Hiragino Sans" if sys.platform == "darwin" else "sans-serif"


def load_items(json_path: Path) -> list[dict]:
    print(f"Loading {json_path}...")
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("入力JSONは記事配列である必要があります。")

    return data


def normalize_items(items: list[dict]) -> pd.DataFrame:
    print(f"Normalizing {len(items)} items...")
    rows = []
    for item in items:
        tags = item.get("tags", [])
        if isinstance(tags, list):
            # タグが辞書のリスト(apiレスポンス)か文字列のリストかを判定
            normalized_tags = [
                t.get("name") if isinstance(t, dict) else str(t) for t in tags
            ]
        else:
            normalized_tags = []

        rows.append(
            {
                "title": item.get("title", ""),
                "likes_count": int(item.get("likes_count", 0) or 0),
                "stocks_count": int(item.get("stocks_count", 0) or 0),
                "created_at": item.get("created_at", ""),
                "url": item.get("url", ""),
                "tags": normalized_tags,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("記事データが空です。")

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df


def save_summary(df: pd.DataFrame, out_dir: Path) -> None:
    print("Saving summary...")
    summary = {
        "articles": len(df),
        "likes_total": int(df["likes_count"].sum()),
        "likes_mean": float(df["likes_count"].mean()),
        "stocks_total": int(df["stocks_count"].sum()),
        "stocks_mean": float(df["stocks_count"].mean()),
        "max_likes": int(df["likes_count"].max()),
        "max_stocks": int(df["stocks_count"].max()),
    }

    summary_df = pd.Series(summary, name="Value").to_frame()
    summary_path = out_dir / "summary.csv"
    summary_df.to_csv(summary_path, encoding="utf-8-sig")


def plot_histograms(df: pd.DataFrame, out_dir: Path) -> None:
    print("Plotting histograms...")
    plt.figure(figsize=(10, 6))
    plt.hist(df["likes_count"], bins=20, color="skyblue", edgecolor="black")
    plt.title("LGTM数分布 (Likes)")
    plt.xlabel("いいね数")
    plt.ylabel("記事数")
    plt.tight_layout()
    plt.savefig(out_dir / "likes_distribution.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.hist(df["stocks_count"], bins=20, color="orange", edgecolor="black")
    plt.title("ストック数分布 (Stocks)")
    plt.xlabel("ストック数")
    plt.ylabel("記事数")
    plt.tight_layout()
    plt.savefig(out_dir / "stocks_distribution.png", dpi=150)
    plt.close()


def plot_top_tags(df: pd.DataFrame, out_dir: Path, top_n: int) -> None:
    print(f"Plotting top {top_n} tags...")
    exploded = df.explode("tags")
    exploded = exploded.dropna(subset=["tags"])
    if exploded.empty:
        return

    tag_counts = exploded["tags"].value_counts().head(top_n)

    plt.figure(figsize=(12, 6))
    tag_counts.sort_values().plot(kind="barh", color="green")
    plt.title(f"上位 {top_n} タグ")
    plt.xlabel("記事数")
    plt.ylabel("タグ名")
    plt.tight_layout()
    plt.savefig(out_dir / "top_tags.png", dpi=150)
    plt.close()


def plot_monthly_trend(df: pd.DataFrame, out_dir: Path) -> None:
    print("Plotting monthly trend...")
    valid_dates = df.dropna(subset=["created_at"]).copy()
    if valid_dates.empty:
        return

    monthly = valid_dates.set_index("created_at").resample("ME").size()

    plt.figure(figsize=(12, 6))
    monthly.plot(marker="s", color="red")
    plt.title("月別投稿数推移")
    plt.xlabel("月")
    plt.ylabel("記事数")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(out_dir / "monthly_trend.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Qiita記事JSONを集計・可視化します。")
    parser.add_argument("input_json", type=str, nargs="?", help="入力JSONファイル")
    parser.add_argument("--out-dir", type=str, default=None, help="出力先ディレクトリ（未指定時はJSON名＋_analysis）")
    parser.add_argument("--top-tags", type=int, default=15, help="タグ集計の上位件数")
    args = parser.parse_args()

    # 引数がない場合は対話形式でファイルを選択
    if args.input_json is None:
        json_files = list(Path(".").glob("*.json"))
        if not json_files:
            print("Error: 実行ディレクトリに .json ファイルが見つかりません。")
            sys.exit(1)

        print("\n--- 分析対象のJSONファイルを選択してください ---")
        for i, f in enumerate(json_files):
            print(f"[{i}] {f}")
        
        try:
            choice = int(input(f"\n番号を入力してください (0-{len(json_files)-1}): "))
            if 0 <= choice < len(json_files):
                input_path = json_files[choice]
            else:
                print("無効な番号です。")
                sys.exit(1)
        except ValueError:
            print("数値を入力してください。")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n取り消されました。")
            sys.exit(0)
    else:
        input_path = Path(args.input_json)

    if not input_path.exists():
        print(f"Error: {input_path} が見つかりません。")
        sys.exit(1)

    # 出力先を決定
    if args.out_dir is None:
        out_dir = input_path.parent / f"{input_path.stem}_analysis"
    else:
        out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    items = load_items(input_path)
    df = normalize_items(items)

    csv_out = out_dir / "articles_full_data.csv"
    print(f"Saving sorted data to {csv_out}...")
    df.sort_values("likes_count", ascending=False).to_csv(
        csv_out, index=False, encoding="utf-8-sig"
    )

    save_summary(df, out_dir)
    plot_histograms(df, out_dir)
    plot_top_tags(df, out_dir, args.top_tags)
    plot_monthly_trend(df, out_dir)

    print(f"分析完了: {out_dir}")


if __name__ == "__main__":
    main()
