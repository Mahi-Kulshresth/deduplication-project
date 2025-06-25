# Steam Deduplication Project

This project tackles the problem of duplicate records in the [Steam-200K dataset](https://www.kaggle.com/datasets/nikdavis/steam-store-games) by cleaning and deduplicating user-game interactions, specifically purchases and play sessions.

---
# Objective

To identify and clean **three types of duplicates** in the dataset:
1. **Exact duplicates** – Entire row repetitions.
2. **Partial duplicates** – Multiple 'play' records for the same user-game.
3. **Fuzzy duplicates** – Slightly varied text entries of the same game (e.g., `GTA V`, `GTA 5`, `Grand Theft Auto V`).

##  Approach

The logic was first explored in a Jupyter notebook with visualizations and then refactored into a reusable Python script. The processing steps include:

## 🧹 Steps Performed

### 1. Data Loading and Initial Checks
- Loaded `steam-200k.csv` (200,000 rows × 5 columns)
- Renamed columns for clarity
- Dropped `extra` column (contained only 0s)

### 2. Missing Value Check
- Confirmed no missing/null values in the dataset

### 3. Exact Deduplication
- Identified and removed `707` fully duplicate rows using `df.duplicated()`

### 4. Partial Deduplication
- For `'play'` behavior:
  - Aggregated total playtime per user-game using `groupby` and `sum`
- For `'purchase'` behavior:
  - Kept a single row per user-game
- Combined both into a unified, deduplicated dataframe

### 5. Fuzzy Deduplication with Sequel Protection
Used RapidFuzz to identify game titles with ≥90% similarity. Applied logic to merge titles only if:

- Titles had no numbers, or

- Had same numeric meaning (e.g., "5", "V", "Five")

- Did not differ in keywords like "DLC", "Bundle", "Episode", "Part", "Mac/Linux/NA/EU"

- Titles like "GTA 5" and "GTA V" were merged
Titles like "Call of Duty 4" and "Call of Duty 3" were skipped

---
## 📊 Results

| Metric                        | Count     |
|------------------------------|-----------|
| Original rows                | 199,999   |
| After exact deduplication    | 199,292   |
| After partial aggregation    | 199,281   |
| Unique game titles before    | 5,151     |
| Unique game titles after     | 5,026     |
| Fuzzy duplicates merged      | 125       |
| Remaining fuzzy-similar pairs| 175       |

---

## Tools Used
- Pandas for data handling

- RapidFuzz for fuzzy matching

- Regex for numeric and keyword extraction

- Matplotlib / Seaborn (optional for visualizations)

---

## 🗃️ Project Structure

steam-deduplication-project/
│
├── data/
│ └── steam-200k.csv # Raw dataset
│
├── results/
│ └── steam_cleaned.csv # Cleaned final output
│
├── notebooks/
│ └── next.ipynb # EDA + visualization
│
├── src/
│ └── deduplicate.py # Main deduplication script
│
└── README.md

##  Running the Script

Make sure `pandas` is installed:

```bash
pip install pandas

Then run from the project root:
python src/deduplicate.py

This will output the cleaned data to results/steam_cleaned.csv.

Author
Mahi Kulshresth
Intern, JK Technosoft Ltd.

License
This project is for learning and evaluation purposes only. Original dataset © Kaggle contributors.
