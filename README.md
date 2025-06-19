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
- Loaded `steam-200k.csv` (199,999 rows × 5 columns)
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
- Used `RapidFuzz` to detect similar game titles (≥90% similarity)
- Preprocessed titles using tokenization and regex
- **Protected sequels** (e.g., `'Call of Duty 2'` vs `'Call of Duty 3'`) using number/roman numeral checks
- Merged fuzzy duplicates **only** when they referred to the same game

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
