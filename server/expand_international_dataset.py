"""
Dataset utility for Smart Recipe Recommender:
1. Maps existing recipes in `recipes_3.csv` to Origin: 'Indian' vs 'Out of India' (International).
2. Provides an automated downloader to fetch additional international recipes from TheMealDB API
   to expand the 'Out of India' collection.
"""

import os
import sys
import io
import time
import requests
import pandas as pd

# Set console output encoding to utf-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INDIAN_CUISINES = {
    'indian', 'north indian recipes', 'south indian recipes', 'maharashtrian recipes',
    'bengali recipes', 'karnataka', 'tamil nadu', 'kerala recipes', 'andhra', 'rajasthani',
    'gujarati recipes', 'goan recipes', 'chettinad', 'punjabi', 'kashmiri', 'mangalorean',
    'parsi recipes', 'awadhi', 'konkan', 'sindhi', 'assamese', 'oriya recipes', 'hyderabadi',
    'mughlai', 'bihari', 'north east india recipes', 'himachal', 'udupi', 'coorg',
    'north karnataka', 'uttar pradesh', 'coastal karnataka', 'malabar', 'lucknowi',
    'south karnataka', 'malvani', 'uttarakhand-north kumaon', 'kongunadu', 'nagaland',
    'haryana', 'jharkhand'
}

def clean_cuisine_name(cuisine: str) -> str:
    if not isinstance(cuisine, str):
        return ""
    # Remove invisible BOM and strip
    return cuisine.replace('\ufeff', '').strip()

def classify_origin(cuisine: str) -> str:
    cleaned = clean_cuisine_name(cuisine).lower()
    if cleaned in INDIAN_CUISINES:
        return 'Indian'
    return 'Out of India'

def inspect_current_dataset(csv_path="server/recipes_3.csv"):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return None
    
    df = pd.read_csv(csv_path)
    df['Cleaned_Cuisine'] = df['Cuisine'].apply(clean_cuisine_name)
    df['DishOrigin'] = df['Cleaned_Cuisine'].apply(classify_origin)
    
    print("=== Current Dataset Breakdown ===")
    print(f"Total recipes: {len(df)}")
    print(f"Indian dishes: {(df['DishOrigin'] == 'Indian').sum()}")
    print(f"Out of India (International) dishes: {(df['DishOrigin'] == 'Out of India').sum()}")
    print("\nTop Out-of-India Cuisines currently in dataset:")
    print(df[df['DishOrigin'] == 'Out of India']['Cleaned_Cuisine'].value_counts().head(15))
    return df

def fetch_themealdb_international_recipes(max_letters=26):
    """
    Fetches international recipes from TheMealDB free open API.
    Covers areas: Italian, Mexican, American, British, French, Chinese, Japanese, Greek, etc.
    """
    print("\nFetching additional Out-of-India recipes from TheMealDB API...")
    import string
    
    meals_collected = []
    seen_names = set()
    
    for letter in string.ascii_lowercase[:max_letters]:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?f={letter}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                meals = data.get('meals') or []
                for m in meals:
                    name = (m.get('strMeal') or '').strip()
                    area = (m.get('strArea') or '').strip()
                    # Skip if area is Indian (we want out of India dishes) or already seen
                    if not name or area.lower() in ('indian', 'unknown') or name in seen_names:
                        continue
                    
                    seen_names.add(name)
                    
                    # Extract ingredients & measures
                    raw_ingredients = []
                    cleaned_ingredients = []
                    for i in range(1, 21):
                        ing = m.get(f'strIngredient{i}')
                        meas = m.get(f'strMeasure{i}')
                        if ing and isinstance(ing, str) and ing.strip():
                            ing = ing.strip()
                            meas = meas.strip() if meas and isinstance(meas, str) else ''
                            raw_ingredients.append(f"{meas} {ing}".strip() if meas else ing)
                            cleaned_ingredients.append(ing.lower())
                    
                    if not cleaned_ingredients:
                        continue
                        
                    instructions = (m.get('strInstructions') or '').strip().replace('\r\n', ' ').replace('\n', ' ')
                    image_url = m.get('strMealThumb') or ''
                    source_url = m.get('strSource') or m.get('strYoutube') or f"https://www.themealdb.com/meal/{m.get('idMeal')}"
                    
                    # Approximate cooking time based on category/ingredients
                    cooking_time = 30
                    cat = (m.get('strCategory') or '').lower()
                    if 'beef' in cat or 'lamb' in cat or 'pork' in cat:
                        cooking_time = 60
                    elif 'dessert' in cat or 'baking' in cat:
                        cooking_time = 45
                    elif 'pasta' in cat or 'seafood' in cat or 'side' in cat:
                        cooking_time = 25
                    
                    meals_collected.append({
                        'TranslatedRecipeName': name,
                        'TranslatedIngredients': ', '.join(raw_ingredients),
                        'TotalTimeInMins': cooking_time,
                        'Cuisine': area if area else 'International',
                        'TranslatedInstructions': instructions,
                        'URL': source_url,
                        'Cleaned-Ingredients': ', '.join(cleaned_ingredients),
                        'image-url': image_url,
                        'Ingredient-count': len(cleaned_ingredients)
                    })
        except Exception as e:
            print(f"Error fetching letter {letter}: {e}")
        time.sleep(0.1)
    
    print(f"Successfully fetched {len(meals_collected)} new international dishes from TheMealDB!")
    return pd.DataFrame(meals_collected)

if __name__ == '__main__':
    df = inspect_current_dataset()
    if len(sys.argv) > 1 and sys.argv[1] == '--fetch-more':
        new_international_df = fetch_themealdb_international_recipes()
        output_path = "server/recipes_expanded.csv"
        merged_df = pd.concat([df.drop(columns=['Cleaned_Cuisine', 'DishOrigin'], errors='ignore'), new_international_df], ignore_index=True)
        merged_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Merged dataset saved to {output_path} (Total: {len(merged_df)} recipes)")
