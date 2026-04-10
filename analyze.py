import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_items(json_path: Path) -> list[dict]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("入力JSONは記事配列である必要があります。")

    return data


def normalize_items(items: list[dict]) -> pd.DataFrame:
    rows = []
    for item in items:
        tags = item.get("tags", [])
        if isinstance(tags, list):
            normalized_tags = [t if isinstance(t, str) else str(t) for t in tags]
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
    summary = {
        "articles": len(df),
        "likes_total": int(df["likes_count"].sum()),
        "likes_mean": float(df["likes_count"].mean()),
        "stocks_total": int(df["stocks_count"].sum()),
        "stocks_mean": float(df["stocks_count"].mean()),
    }

    summary_df = pd.DataFrame([summary])
    summary_path = out_dir / "summary.csv"
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")


def plot_histograms(df: pd.DataFrame, out_dir: Path) -> None:
    plt.figure(figsize=(10, 6))
    plt.hist(df["likes_count"], bins=20)
    plt.title("Likes Distribution")
    plt.xlabel("likes_count")
    plt.ylabel("articles")
    plt.tight_layout()
    plt.savefig(out_dir / "likes_distribution.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.hist(df["stocks_count"], bins=20)
    plt.title("Stocks Distribution")
    plt.xlabel("stocks_count")
    plt.ylabel("articles")
    plt.tight_layout()
    plt.savefig(out_dir / "stocks_distribution.png", dpi=150)
    plt.close()


def plot_top_tags(df: pd.DataFrame, out_dir: Path, top_n: int) -> None:
    exploded = df.explode("tags")
    exploded = exploded.dropna(subset=["tags"])
    if exploded.empty:
        return

    tag_counts = exploded["tags"].value_counts().head(top_n)

    plt.figure(figsize=(10, 6))
    tag_counts.sort_values().plot(kind="barh")
    plt.title(f"Top {top_n} Tags")
    plt.xlabel("articles")
    plt.ylabel("tag")
    plt.tight_layout()
    plt.savefig(out_dir / "top_tags.png", dpi=150)
    plt.close()


def plot_monthly_trend(df: pd.DataFrame, out_dir: Path) -> None:
    valid_dates = df.dropna(subset=["created_at"]).copy()
    if valid_dates.empty:
        return

    monthly = valid_dates.set_index("created_at").resample("ME").size()

    plt.figure(figsize=(10, 6))
    monthly.plot(marker="o")
    plt.title("Monthly Article Count")
    plt.xlabel("month")
    plt.ylabel("articles")
    plt.tight_layout()
    plt.savefig(out_dir / "monthly_trend.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Qiita記事JSONを集計・可視化します。")
    parser.add_argument("input_json", type=str, help="入力JSONファイル")
    parser.add_argument("--out-dir", type=str, default="analysis_output", help="出力先ディレクトリ")
    parser.add_argument("--top-tags", type=int, default=10, help="タグ集計の上位件数")
    args = parser.parse_args()

    input_path = Path(args.input_json)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    items = load_items(input_path)
    df = normalize_items(items)

    df.sort_values("likes_count", ascending=False).to_csv(
        out_dir / "articles_sorted_by_likes.csv", index=False, encoding="utf-8-sig"
    )

    save_summary(df, out_dir)
    plot_histograms(df, out_dir)
    plot_top_tags(df, out_dir, args.top_tags)
    plot_monthly_trend(df, out_dir)

    print(f"分析完了: {out_dir}")


if __name__ == "__main__":
    main()
