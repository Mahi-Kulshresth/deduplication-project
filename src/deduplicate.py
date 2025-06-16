import os
import pandas as pd

def load_data(path):
    df=pd.read_csv(path, header=None)
    df.columns=['user-id', 'game-title', 'behaviour', 'value', 'extra']
    df=df.drop(columns=['extra'])
    return df

def remove_exact_duplicates(df):
    return df.drop_duplicates()

def deduplicate_actions(df):
    purchases=df[df['behaviour']=='purchase']
    purchases_cleaned= purchases.drop_duplicates(subset=['user-id','game-title'])

    plays=df[df['behaviour']== 'play']
    plays_cleaned= plays.groupby(['user-id', 'game-title']).agg({'value': 'sum'}).reset_index()
    plays_cleaned['behaviour']= 'play'

    plays_cleaned = plays_cleaned[['user-id', 'game-title', 'behaviour', 'value']]

    final_df = pd.concat([purchases_cleaned, plays_cleaned], ignore_index=True)
    return final_df

def save_data(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)

def main():
    input_path = 'data/steam-200k.csv'
    output_path = 'results/steam_cleaned.csv'

    print("Loading data...")
    data = load_data(input_path)

    print("Removing exact duplicates...")
    data = remove_exact_duplicates(data)

    print("Deduplicating actions...")
    final_df = deduplicate_actions(data)

    print("Saving cleaned data...")
    save_data(final_df, output_path)

    print(f"Done! Final shape: {final_df.shape}")


if __name__ == "__main__":
    main()