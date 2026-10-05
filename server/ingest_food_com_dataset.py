"""
Ingestion script to extract high-quality international recipes from the Food.com dataset
(recipes/RAW_recipes.csv) and merge them with our existing dataset.
"""

import os
import sys
import io
import ast
import pandas as pd

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RAW_RECIPES_PATH = "recipes/RAW_recipes.csv"
EXPANDED_PATH = "server/recipes_expanded.csv"
OUTPUT_PATH = "server/recipes_expanded.csv"

CUISINE_MAP = {
    'italian': 'Italian Recipes',
    'mexican': 'Mexican',
    'french': 'French',
    'chinese': 'Chinese',
    'japanese': 'Japanese',
    'greek': 'Greek',
    'spanish': 'Spanish',
    'thai': 'Thai',
    'asian': 'Asian',
    'mediterranean': 'Mediterranean',
    'korean': 'Korean',
    'german': 'German',
    'british': 'British'
}

def extract_cuisine(tags_list):
    for tag in tags_list:
        t = tag.lower().strip()
        if t in CUISINE_MAP:
            return CUISINE_MAP[t]
    return None

def ingest_food_com_recipes(target_count=3500):
    if not os.path.exists(RAW_RECIPES_PATH):
        print(f"Error: {RAW_RECIPES_PATH} not found.")
        return None

    print(f"[*] Reading {RAW_RECIPES_PATH}...")
    # Load required columns
    df = pd.read_csv(
        RAW_RECIPES_PATH,
        usecols=['id', 'name', 'minutes', 'tags', 'steps', 'ingredients', 'n_ingredients', 'n_steps']
    )
    print(f"[*] Total raw recipes in Food.com dataset: {len(df):,}")

    # Basic filter: reasonable cook time and ingredient count
    df = df[
        (df['minutes'] >= 5) & (df['minutes'] <= 60) &
        (df['n_ingredients'] >= 3) & (df['n_ingredients'] <= 12) &
        (df['n_steps'] >= 2) & (df['n_steps'] <= 15) &
        (df['name'].notna()) & (df['name'].str.len() > 3)
    ]
    print(f"[*] Recipes matching time/complexity constraints: {len(df):,}")

    # Parse cuisines
    collected = []
    seen_names = set()
    
    # Check if expanded already exists to avoid duplicate names
    if os.path.exists(EXPANDED_PATH):
        existing_df = pd.read_csv(EXPANDED_PATH)
        for n in existing_df['TranslatedRecipeName'].dropna():
            seen_names.add(str(n).lower().strip())
        print(f"[*] Existing dataset has {len(existing_df):,} recipes.")
    else:
        existing_df = None

    for _, row in df.iterrows():
        name = str(row['name']).strip().title()
        if name.lower() in seen_names:
            continue

        try:
            tags = ast.literal_eval(row['tags'])
            cuisine = extract_cuisine(tags)
            if not cuisine:
                continue

            steps = ast.literal_eval(row['steps'])
            ingredients = ast.literal_eval(row['ingredients'])
            
            if not steps or not ingredients:
                continue

            seen_names.add(name.lower())
            
            # Format instructions cleanly
            instructions = ". ".join([s.strip().capitalize() for s in steps if s.strip()]) + "."
            cleaned_ingredients = ", ".join([ing.lower().strip() for ing in ingredients])
            url = f"https://www.food.com/recipe/{row['id']}"

            collected.append({
                'TranslatedRecipeName': name,
                'TranslatedIngredients': cleaned_ingredients,
                'TotalTimeInMins': int(row['minutes']),
                'Cuisine': cuisine,
                'TranslatedInstructions': instructions,
                'URL': url,
                'Cleaned-Ingredients': cleaned_ingredients,
                'image-url': '',
                'Ingredient-count': int(row['n_ingredients'])
            })

            if len(collected) >= target_count:
                break
        except Exception:
            continue

    print(f"[*] Successfully curated {len(collected):,} premium international recipes from Food.com!")
    new_df = pd.DataFrame(collected)

    if existing_df is not None:
        merged_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        merged_df = new_df

    print(f"[*] Merged total recipes: {len(merged_df):,}")
    merged_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    print(f"[*] Saved enriched dataset to {OUTPUT_PATH}")
    return merged_df

if __name__ == '__main__':
    ingest_food_com_recipes(target_count=3500)
