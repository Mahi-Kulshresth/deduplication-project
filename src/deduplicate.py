import pandas as pd
import re
from rapidfuzz import process, fuzz
from collections import defaultdict
import os

digit_word_map = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5",
    "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10"
}
conflict_keywords = ["dlc", "bundle", "mac", "linux", "asia", "japan", "episode", "season", "expansion", "pack"]

def normalize_title(title):
    title = title.lower()
    for word, digit in digit_word_map.items():
        title = re.sub(rf"\b{re.escape(word)}\b", digit, title)
    return title

def extract_numbers_with_tokens(title):
    title = normalize_title(title)
    tokens = title.split()
    result = []
    for i, token in enumerate(tokens):
        if token.isdigit():
            prev = tokens[i - 1] if i > 0 else ""
            if prev in conflict_keywords:
                result.append((prev, int(token)))
            else:
                result.append(("", int(token)))
    return result

def safe_to_merge(title1, title2):
    t1, t2 = normalize_title(title1), normalize_title(title2)

    nums1 = extract_numbers_with_tokens(t1)
    nums2 = extract_numbers_with_tokens(t2)

    for (k1, n1) in nums1:
        for (k2, n2) in nums2:
            if k1 == k2 and n1 != n2 and k1 != "":
                return False

    plain_nums1 = {n for (k, n) in nums1 if k == ""}
    plain_nums2 = {n for (k, n) in nums2 if k == ""}

    if plain_nums1 and plain_nums2 and plain_nums1 != plain_nums2:
        return False

    if (plain_nums1 and not plain_nums2) or (plain_nums2 and not plain_nums1):
        return False

    for word in conflict_keywords:
        if (word in t1 and word not in t2) or (word in t2 and word not in t1):
            return False

    similarity = fuzz.token_set_ratio(t1, t2)
    return similarity >= 85

# --- Preprocessing still used for title cleanup ---
def preprocess_title(title):
    title = title.lower()
    title = re.sub(r'[\W_]+', ' ', title)
    return title.strip()

def fuzzy_deduplicate(df):
    df['clean-title'] = df['game-title'].apply(preprocess_title)
    clean_titles = df['clean-title'].unique().tolist()

    cluster_map = {}
    seen = set()

    for title in clean_titles:
        if title in seen:
            continue

        # RapidFuzz: Only get top 10 similar titles
        matches = process.extract(
            query=title,
            choices=clean_titles,
            scorer=fuzz.token_set_ratio,
            limit=10
        )

        group = [m[0] for m in matches if safe_to_merge(title, m[0])]
        canonical = sorted(group, key=lambda x: (len(x), x))[0]
        for dup in group:
            cluster_map[dup] = canonical
            seen.add(dup)

    df['canonical-title'] = df['clean-title'].map(cluster_map)
    df['game-title'] = df['canonical-title'].fillna(df['clean-title']).str.title()
    df.drop(columns=['clean-title', 'canonical-title'], inplace=True)

    before = len(clean_titles)
    after = df['game-title'].nunique()
    print(f" Fuzzy Deduplication: {before - after} titles merged ({before} → {after})")

    return df

def count_fuzzy_duplicate_pairs(titles):
    count = 0
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            if safe_to_merge(titles[i], titles[j]):
                count += 1
    return count


def main():
    input_path = 'data/steam-200k.csv'
    output_path = 'results/steam_cleaned.csv'

    print(" Loading data...")
    df = pd.read_csv(input_path, header=None)
    df.columns = ['user-id', 'game-title', 'behavior', 'value', 'extra']
    print(f"Initial shape: {df.shape}")

    print("\n Missing values:\n", df.isnull().sum())

    if df['extra'].nunique() == 1:
        df.drop(columns=['extra'], inplace=True)
    print(f"Shape after dropping 'extra': {df.shape}")

    exact_dupes = df.duplicated().sum()
    print(f"\n Exact duplicate rows: {exact_dupes}")
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
