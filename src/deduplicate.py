import pandas as pd
import re
from rapidfuzz import process, fuzz
from collections import defaultdict
import os

def preprocess_title(title):
    title = title.lower()
    title = re.sub(r'[\W_]+', ' ', title)
    return title.strip()

def is_probably_sequel(t1, t2):
    pattern = r'\b([ivx]+|\d+)\b'
    n1 = re.findall(pattern, t1.lower())
    n2 = re.findall(pattern, t2.lower())
    return bool(n1 and n2 and n1 != n2)

def fuzzy_deduplicate(df):
    df['clean-title'] = df['game-title'].apply(preprocess_title)
    clean_titles = df['clean-title'].unique()

    cluster_map = {}
    for title in clean_titles:
        if title in cluster_map:
            continue
        matches = process.extract(title, clean_titles, scorer=fuzz.token_sort_ratio, limit=None)
        similar_titles = [m for m, score, _ in matches if score >= 90 and not is_probably_sequel(title, m)]
        canonical = max(similar_titles, key=len)
        for dup in similar_titles:
            cluster_map[dup] = canonical

    df['canonical-title'] = df['clean-title'].map(cluster_map)
    df['game-title'] = df['canonical-title'].fillna(df['clean-title']).str.title()
    df.drop(columns=['clean-title', 'canonical-title'], inplace=True)

    before = len(clean_titles)
    after = df['game-title'].nunique()
    print(f" Fuzzy Deduplication Results: {before - after} titles merged (from {before} → {after})")

    return df

def count_fuzzy_duplicate_pairs(titles):
    count = 0
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            if fuzz.token_sort_ratio(titles[i], titles[j]) >= 90:
                count += 1
    return count

def main():
    input_path = 'data/steam-200k.csv'
    output_path = 'results/steam_cleaned.csv'

    print(" Loading data...")
    df = pd.read_csv(input_path, header=None)
    df.columns = ['user-id', 'game-title', 'behavior', 'value', 'extra']
    print(f"Initial shape: {df.shape}")

    print("\n🔍 Missing values:\n", df.isnull().sum())

    if df['extra'].nunique() == 1:
        df.drop(columns=['extra'], inplace=True)
    print(f"Shape after dropping 'extra': {df.shape}")

    exact_dupes = df.duplicated().sum()
    print(f"\n🧹 Exact duplicate rows: {exact_dupes}")
    df.drop_duplicates(inplace=True)
    print(f"Shape after exact deduplication: {df.shape}")

    plays = df[df['behavior'] == 'play']
    purchases = df[df['behavior'] == 'purchase']
    plays_cleaned = plays.groupby(['user-id', 'game-title'], as_index=False)['value'].sum()
    df = pd.concat([purchases, plays_cleaned], ignore_index=True).sort_values(by=['user-id', 'game-title']).reset_index(drop=True)
    print(f"Shape after aggregating 'play' actions: {df.shape}")

    df = fuzzy_deduplicate(df)

    fuzzy_pairs = count_fuzzy_duplicate_pairs(df['game-title'].unique())
    print(f" Remaining fuzzy duplicate title pairs (≥90% similarity): {fuzzy_pairs}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n Final cleaned dataset saved to '{output_path}' with shape: {df.shape}")

if __name__ == "__main__":
    main()
