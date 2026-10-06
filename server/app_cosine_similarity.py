import os
import re
import ast
import time
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------
# Dataset Loading & Cache Architecture
# ---------------------------------------------------------
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SERVER_DIR)
CLIENT_DIR = os.path.join(PROJECT_DIR, "client")

expanded_csv = os.path.join(SERVER_DIR, "recipes_expanded.csv")
base_csv = os.path.join(SERVER_DIR, "recipes_3.csv")
DATASET_PATH = expanded_csv if os.path.exists(expanded_csv) else (
    base_csv if os.path.exists(base_csv) else ("server/recipes_expanded.csv" if os.path.exists("server/recipes_expanded.csv") else "server/recipes_3.csv")
)
CACHE_DIR = os.path.join(SERVER_DIR, "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "recommender_cache.joblib")

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

CULINARY_STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by',
    'teaspoon', 'teaspoons', 'tsp', 'tablespoon', 'tablespoons', 'tbsp',
    'cup', 'cups', 'gram', 'grams', 'g', 'kg', 'ml', 'liter', 'liters', 'oz', 'ounce', 'ounces',
    'pinch', 'pinches', 'taste', 'required', 'needed', 'optional', 'fresh', 'dry', 'dried',
    'chopped', 'sliced', 'diced', 'minced', 'peeled', 'crushed', 'grated', 'shredded',
    'ground', 'powder', 'paste', 'leaves', 'leaf', 'medium', 'small', 'large', 'finely',
    'roughly', 'coarsely', 'boiled', 'cooked', 'warm', 'hot', 'cold', 'water', 'salt', 'oil'
}

PLURAL_MAP = {
    'tomatoes': 'tomato', 'potatoes': 'potato', 'onions': 'onion', 'chillies': 'chilli',
    'chiles': 'chilli', 'chilies': 'chilli', 'leaves': 'leaf', 'cloves': 'clove',
    'eggs': 'egg', 'carrots': 'carrot', 'beans': 'bean', 'mushrooms': 'mushroom',
    'noodles': 'noodle', 'breasts': 'breast', 'thighs': 'thigh', 'peppers': 'pepper',
    'lemons': 'lemon', 'limes': 'lime', 'apples': 'apple', 'bananas': 'banana'
}

def clean_cuisine_name(cuisine: str) -> str:
    if not isinstance(cuisine, str):
        return "Other"
    return cuisine.replace('\ufeff', '').strip()

def classify_origin(cuisine: str) -> str:
    cleaned = clean_cuisine_name(cuisine).lower()
    if cleaned in INDIAN_CUISINES:
        return 'Indian'
    return 'Out of India'

def normalize_token(token: str) -> str:
    token = token.lower().strip()
    if token in PLURAL_MAP:
        return PLURAL_MAP[token]
    if token.endswith('ies') and len(token) > 4:
        return token[:-3] + 'y'
    if token.endswith('es') and len(token) > 3 and not token.endswith('ches') and not token.endswith('shes'):
        return token[:-2]
    if token.endswith('s') and len(token) > 3 and not token.endswith('ss'):
        return token[:-1]
    return token

def preprocess_ingredient_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    tokens = re.findall(r'[a-zA-Z]+', text.lower())
    cleaned_tokens = []
    for tok in tokens:
        tok_norm = normalize_token(tok)
        if tok_norm not in CULINARY_STOPWORDS and len(tok_norm) > 2:
            cleaned_tokens.append(tok_norm)
    return " ".join(cleaned_tokens)

def extract_ingredient_list(raw_val):
    if isinstance(raw_val, str):
        raw_val = raw_val.strip()
        if raw_val.startswith('[') and raw_val.endswith(']'):
            try:
                parsed = ast.literal_eval(raw_val)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass
        return [x.strip() for x in raw_val.split(',') if x.strip()]
    elif isinstance(raw_val, (list, tuple)):
        return [str(x).strip() for x in raw_val if str(x).strip()]
    return []

def extract_instruction_steps(raw_val):
    if not isinstance(raw_val, str):
        return []
    raw_val = raw_val.replace('\r\n', '\n').strip()
    lines = [line.strip() for line in raw_val.split('\n') if line.strip()]
    if len(lines) > 1:
        return lines
    steps = [s.strip() for s in re.split(r'\.\s+', raw_val) if s.strip()]
    return steps if steps else [raw_val]

def load_data_and_model():
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_valid = False
    
    if os.path.exists(CACHE_FILE) and os.path.exists(DATASET_PATH):
        if os.path.getmtime(CACHE_FILE) >= os.path.getmtime(DATASET_PATH):
            cache_valid = True

    if cache_valid:
        t0 = time.time()
        print(f"[*] Fast-loading precomputed model from cache: {CACHE_FILE}")
        cache_data = joblib.load(CACHE_FILE)
        df = cache_data['df']
        vectorizer = cache_data['vectorizer']
        matrix = cache_data['matrix']
        print(f"[*] Loaded {len(df):,} recipes in {time.time()-t0:.2f} seconds!")
        return df, vectorizer, matrix
    
    t0 = time.time()
    print(f"[*] Cache miss or dataset updated. Loading dataset: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    
    df['Cleaned_Cuisine'] = df['Cuisine'].apply(clean_cuisine_name)
    df['DishOrigin'] = df['Cleaned_Cuisine'].apply(classify_origin)
    df['TotalTimeInMins'] = pd.to_numeric(df['TotalTimeInMins'], errors='coerce').fillna(30).astype(int)
    df['Ingredient-count'] = pd.to_numeric(df['Ingredient-count'], errors='coerce').fillna(8).astype(int)
    
    print("[*] Preprocessing ingredients for TF-IDF...")
    df['Processed_Ingredients'] = df['Cleaned-Ingredients'].apply(preprocess_ingredient_text)
    
    print("[*] Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=15000)
    matrix = vectorizer.fit_transform(df['Processed_Ingredients'].tolist())
    
    print(f"[*] Saving cache to {CACHE_FILE}...")
    joblib.dump({'df': df, 'vectorizer': vectorizer, 'matrix': matrix}, CACHE_FILE, compress=3)
    print(f"[*] Processed and cached {len(df):,} recipes in {time.time()-t0:.2f} seconds!")
    return df, vectorizer, matrix

df, tfidf_vectorizer, tfidf_matrix = load_data_and_model()

# ---------------------------------------------------------
# Recommendation Engine Logic
# ---------------------------------------------------------
DIETARY_EXCLUSIONS = {
    'vegetarian': {'chicken', 'beef', 'pork', 'mutton', 'lamb', 'fish', 'prawn', 'shrimp', 'seafood', 'meat', 'bacon', 'ham', 'crab', 'squid'},
    'vegan': {'chicken', 'beef', 'pork', 'mutton', 'lamb', 'fish', 'prawn', 'shrimp', 'seafood', 'meat', 'bacon', 'ham', 'crab',
              'egg', 'eggs', 'milk', 'cheese', 'butter', 'paneer', 'curd', 'yogurt', 'cream', 'ghee', 'honey', 'mayonnaise'},
    'gluten_free': {'flour', 'wheat', 'bread', 'maida', 'atta', 'pasta', 'spaghetti', 'noodle', 'noodles', 'barley', 'semolina', 'suji', 'rava'}
}

def recommend_recipes(user_ingredients, origin='all', cuisine=None, max_time=None, max_ingredients=None, dietary=None, max_missing=None, limit=12):
    if isinstance(user_ingredients, list):
        input_str = " ".join(user_ingredients)
        raw_user_tokens = set(normalize_token(t) for ing in user_ingredients for t in re.findall(r'[a-zA-Z]+', str(ing)))
    else:
        input_str = str(user_ingredients)
        raw_user_tokens = set(normalize_token(t) for t in re.findall(r'[a-zA-Z]+', input_str))
    
    processed_input = preprocess_ingredient_text(input_str)
    if not processed_input:
        return []
    
    user_vector = tfidf_vectorizer.transform([processed_input])
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
    
    # Filter mask
    mask = np.ones(len(df), dtype=bool)
    
    # 1. Origin Filter
    if origin == 'indian':
        mask &= (df['DishOrigin'] == 'Indian')
    elif origin in ('out_of_india', 'international'):
        mask &= (df['DishOrigin'] == 'Out of India')
    
    # 2. Cuisine Filter
    if cuisine and cuisine.lower() not in ('all', '', 'any'):
        mask &= (df['Cleaned_Cuisine'].str.lower() == cuisine.strip().lower())
        
    # 3. Max Time Filter
    if max_time and int(max_time) > 0:
        mask &= (df['TotalTimeInMins'] <= int(max_time))
        
    # 4. Max Ingredients Filter
    if max_ingredients and int(max_ingredients) > 0:
        mask &= (df['Ingredient-count'] <= int(max_ingredients))
        
    # 5. Dietary Filter
    if dietary:
        if isinstance(dietary, str):
            dietary = [dietary]
        for diet in dietary:
            diet_key = diet.lower().replace('-', '_').replace(' ', '_')
            if diet_key in DIETARY_EXCLUSIONS:
                forbidden_words = DIETARY_EXCLUSIONS[diet_key]
                forbid_regex = r'\b(?:' + '|'.join(forbidden_words) + r')\b'
                has_forbidden = df['Processed_Ingredients'].str.contains(forbid_regex, regex=True, case=False)
                mask &= (~has_forbidden)
    
    candidate_indices = np.where(mask)[0]
    if len(candidate_indices) == 0:
        return []
    
    candidate_sims = similarities[candidate_indices]
    
    # Pre-select top candidate indices by similarity
    top_k = min(len(candidate_indices), max(limit * 8, 80))
    top_candidate_order = np.argsort(candidate_sims)[::-1][:top_k]
    selected_indices = candidate_indices[top_candidate_order]
    
    results = []
    user_filtered_tokens = set(processed_input.split())
    
    for idx in selected_indices:
        row = df.iloc[idx]
        sim = float(similarities[idx])
        
        recipe_ing_list = extract_ingredient_list(row['Cleaned-Ingredients'])
        recipe_ing_tokens = [set(preprocess_ingredient_text(item).split()) for item in recipe_ing_list]
        
        matched_ingredients = []
        missing_ingredients = []
        
        for orig_item, token_set in zip(recipe_ing_list, recipe_ing_tokens):
            if token_set & user_filtered_tokens or token_set & raw_user_tokens:
                matched_ingredients.append(orig_item)
            else:
                missing_ingredients.append(orig_item)
                
        # Optional: "Almost There" filter (missing <= max_missing)
        if max_missing is not None and int(max_missing) > 0:
            if len(missing_ingredients) > int(max_missing):
                continue

        total_recipe_ings = max(len(recipe_ing_list), 1)
        coverage = len(matched_ingredients) / total_recipe_ings
        
        time_score = 1.0 if row['TotalTimeInMins'] <= 45 else 0.8
        raw_score = (0.60 * sim) + (0.25 * coverage) + (0.10 * (1.0 if sim > 0.05 else 0.0)) + (0.05 * time_score)
        match_score = int(np.clip(round(raw_score * 100), 5, 99))
        
        image_url = str(row['image-url']).strip() if pd.notna(row['image-url']) else ""
        if not image_url.startswith("http"):
            image_url = ""
            
        results.append({
            "name": row['TranslatedRecipeName'],
            "origin": row['DishOrigin'],
            "cuisine": row['Cleaned_Cuisine'],
            "match_score": match_score,
            "raw_score": raw_score,
            "matched_ingredients": matched_ingredients[:10],
            "missing_ingredients": missing_ingredients[:15],
            "ingredients": recipe_ing_list,
            "instructions": extract_instruction_steps(row['TranslatedInstructions']),
            "total_time_minutes": int(row['TotalTimeInMins']),
            "ingredient_count": int(row['Ingredient-count']),
            "image_url": image_url,
            "source_url": str(row['URL']) if pd.notna(row['URL']) else ""
        })
        
    results.sort(key=lambda x: x['raw_score'], reverse=True)
    return results[:limit]

def find_similar_recipes(recipe_name, limit=3):
    matches = df[df['TranslatedRecipeName'].str.lower() == recipe_name.strip().lower()]
    if len(matches) == 0:
        # Partial match
        matches = df[df['TranslatedRecipeName'].str.contains(re.escape(recipe_name.strip()), case=False, na=False)]
        if len(matches) == 0:
            return []
            
    target_label = matches.index[0]
    target_idx = int(np.flatnonzero(df.index == target_label)[0])
    target_vector = tfidf_matrix.getrow(target_idx)
    
    sims = cosine_similarity(target_vector, tfidf_matrix).flatten()
    sims[target_idx] = -1.0  # Exclude self
    
    top_indices = sims.argsort()[::-1][:limit]
    
    similar_list = []
    for idx in top_indices:
        r = df.iloc[idx]
        image_url = str(r['image-url']).strip() if pd.notna(r['image-url']) else ""
        if not image_url.startswith("http"):
            image_url = ""
            
        similar_list.append({
            "name": r['TranslatedRecipeName'],
            "origin": r['DishOrigin'],
            "cuisine": r['Cleaned_Cuisine'],
            "total_time_minutes": int(r['TotalTimeInMins']),
            "ingredient_count": int(r['Ingredient-count']),
            "image_url": image_url,
            "similarity": round(float(sims[idx]), 2)
        })
    return similar_list

# ---------------------------------------------------------
# Web & API Endpoints
# ---------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return send_from_directory(CLIENT_DIR, 'recipe_recommender.html')

@app.route('/client/<path:filename>', methods=['GET'])
def static_client(filename):
    return send_from_directory(CLIENT_DIR, filename)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "dataset": os.path.basename(DATASET_PATH),
        "total_recipes": len(df),
        "indian_count": int((df['DishOrigin'] == 'Indian').sum()),
        "international_count": int((df['DishOrigin'] == 'Out of India').sum()),
        "cache_enabled": os.path.exists(CACHE_FILE)
    })

@app.route('/api/cuisines', methods=['GET'])
def get_cuisines():
    origin = request.args.get('origin', 'all').lower()
    if origin == 'indian':
        sub_df = df[df['DishOrigin'] == 'Indian']
    elif origin in ('out_of_india', 'international'):
        sub_df = df[df['DishOrigin'] == 'Out of India']
    else:
        sub_df = df
        
    cuisines = sorted(list(sub_df['Cleaned_Cuisine'].dropna().unique()))
    return jsonify({
        "origin": origin,
        "count": len(cuisines),
        "cuisines": cuisines
    })

@app.route('/api/recommend-recipes', methods=['POST'])
def recommend_api():
    if not request.is_json:
        return jsonify({"error": "Request body must be valid JSON"}), 400
        
    data = request.get_json()
    ingredients = data.get('ingredients')
    
    if not ingredients:
        return jsonify({"error": "Please provide at least one ingredient."}), 400
        
    origin = data.get('origin', 'all').lower()
    cuisine = data.get('cuisine')
    max_time = data.get('max_time')
    max_ingredients = data.get('max_ingredients')
    dietary = data.get('dietary', [])
    max_missing = data.get('max_missing')
    limit = min(int(data.get('limit', 12)), 50)
    
    try:
        results = recommend_recipes(
            user_ingredients=ingredients,
            origin=origin,
            cuisine=cuisine,
            max_time=max_time,
            max_ingredients=max_ingredients,
            dietary=dietary,
            max_missing=max_missing,
            limit=limit
        )
        return jsonify({
            "results": results,
            "count": len(results),
            "origin": origin,
            "filters": {
                "cuisine": cuisine,
                "max_time": max_time,
                "dietary": dietary,
                "max_missing": max_missing
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to calculate recommendations: {str(e)}"}), 500

@app.route('/api/similar-recipes', methods=['GET'])
def similar_recipes_api():
    name = request.args.get('name', '').strip()
    if not name:
        return jsonify({"error": "Recipe name is required"}), 400
    limit = min(int(request.args.get('limit', 3)), 10)
    try:
        sims = find_similar_recipes(name, limit=limit)
        return jsonify({
            "query": name,
            "count": len(sims),
            "similar_recipes": sims
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)