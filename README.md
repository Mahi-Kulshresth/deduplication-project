# Steam Deduplication Project

This project tackles the problem of duplicate records in the [Steam-200K dataset](https://www.kaggle.com/datasets/nikdavis/steam-store-games) by cleaning and deduplicating user-game interactions, specifically purchases and play sessions.

---

## Problem Statement

The dataset contains logs of user actions (`purchase`, `play`) along with the time spent (if any). However, multiple entries for the same user-game pair exist, especially for play sessions. The goal is to:

- Remove exact duplicates
- Keep only one `purchase` per user-game
- Aggregate total `play` time per user-game

---

##  Approach

The logic was first explored in a Jupyter notebook with visualizations and then refactored into a reusable Python script. The processing steps include:

1. **Data Loading & Inspection**
2. **Dropping Non-Informative Columns**
3. **Removing Exact Duplicate Rows**
4. **Deduplicating Purchase Entries**
5. **Aggregating Playtime Across Sessions**
6. **Combining Cleaned Data**
7. **Saving to CSV**

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
│ └── 01_data_exploration.ipynb # EDA + visualization
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
