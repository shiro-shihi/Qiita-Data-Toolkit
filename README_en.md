# Qiita Data Toolkit

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Qiita API](https://img.shields.io/badge/Qiita%20API-v2-active)
![Libraries](https://img.shields.io/badge/dependencies-3-blue)
![Repo Size](https://img.shields.io/github/repo-size/shiro-shihi/Qiita-Data-Toolkit)
![Last Commit](https://img.shields.io/github/last-commit/shiro-shihi/Qiita-Data-Toolkit)

A set of CLI tools for fetching, searching, analyzing, and visualizing Qiita articles.

[日本語の README はこちら](README.md)

This project was created for personal development and analysis purposes. You are free to fork or modify the code as needed. However, please maintain the copyright and license notices in accordance with the [MIT License](LICENSE.md).

## Intended Use Cases

- Analyzing trends of popular articles
- Investigating technology trends by tag
- Strategy analysis for Qiita contributions
- Use as a dataset for practicing data analysis

## Project Structure

```text
.
├── analyze.py        # Aggregation and visualization of fetched data
├── search.py         # Search and fetch articles with specific conditions
├── users.py          # Fetch article lists for specific users
├── requirements.txt  # List of dependencies
├── LICENSE.md        # MIT License details
└── README.md         # Japanese documentation
```

## Setup

### 1. Install Dependencies

You can install all necessary libraries using `requirements.txt`.

```bash
pip install -r requirements.txt
```

To install them individually:

```bash
pip install requests pandas matplotlib
```

### 2. Access Token Configuration (Recommended)

Providing an access token is recommended to avoid Qiita API rate limits.

- **Automatic (Recommended)**: Run any script directly. If no token is set, you will be prompted to enter one. Choosing "Save" will automatically generate a `.env` file, so you won't need to enter it again.
- **Environment Variable**: Set the `QIITA_TOKEN` environment variable on your system.
- **Manual**: Create a `.env` file yourself and add the following:

  ```text
  QIITA_TOKEN=your_access_token_here
  ```

> [!NOTE]
> To lower the entry barrier for beginners, this project handles `.env` loading and generation using standard Python features without external libraries like `python-dotenv`. This allows you to start using it immediately without extra installations.

## Usage

### Fetch User Articles

Run [users.py](users.py) and specify the Qiita User ID.

```bash
# Interactive mode (no arguments)
python users.py

# Direct execution with options (e.g., user 'qiita', 50+ likes)
python users.py qiita --likes 50 --sort 1
```

### Search Articles with Conditions

Use [search.py](search.py) to fetch articles matching criteria such as year or minimum stock count.

```bash
# Interactive mode (no arguments)
python search.py

# Direct execution with options (e.g., Year 2024, 500+ stocks, 100+ likes, Tag: Python)
python search.py --year 2024 --stocks 500 --likes 100 --tag Python

# Specify an arbitrary query (e.g., articles with 'python' tag and 1000+ total stocks)
python search.py --query "tag:python stocks:>1000"

# Specify sort order (likes/stocks/created)
python search.py --sort stocks
```

### Analyze & Visualize Data

Use [analyze.py](analyze.py) to aggregate and visualize (graph) the fetched JSON files.

```bash
# Interactive mode: Select a file to analyze (Recommended)
python analyze.py

# Specify a specific file directly
python analyze.py qiita_search_res_20260410_120000.json

# Specify output directory and number of top tags
python analyze.py data.json --out-dir my_report --top-tags 20
```

Main Output Files:

- `analysis_output/articles_sorted_by_likes.csv`
- `analysis_output/summary.csv`
- `analysis_output/likes_distribution.png`
- `analysis_output/stocks_distribution.png`
- `analysis_output/top_tags.png`
- `analysis_output/monthly_trend.png`

## Notes

- This tool uses the [Qiita API v2](https://qiita.com/api/v2/docs). Please comply with the [Qiita Terms of Service](https://qiita.com/terms) when using it.
- Be mindful of the API rate limits.
- For inquiries regarding this tool, please contact [info@shihiro.com](mailto:info@shihiro.com).
- If there is a request for removal from Qiita Inc., we will immediately stop distribution or delete the repository.

## Development & Contribution

If you have suggestions for improvements or new features, please feel free to send a Pull Request! Bug reports are also welcome.

## License

This project is released under the [MIT License](LICENSE.md).

The licenses for the major libraries used in this project are as follows:

- [requests](https://github.com/psf/requests) (Apache License 2.0)
- [pandas](https://github.com/pandas-dev/pandas) (BSD 3-Clause License)
- [matplotlib](https://github.com/matplotlib/matplotlib) (Matplotlib License)

Copyright (c) 2026 shihiro.com
