import sys
import io
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app_cosine_similarity import app

def run_advanced_tests():
    client = app.test_client()
    
    print("\n--- Test 1: Health & Dataset Size ---")
    res = client.get('/api/health')
    data = res.get_json()
    print("Health Status:", res.status_code)
    print("Total Recipes:", data.get('total_recipes'))
    print("Indian Recipes:", data.get('indian_count'))
    print("International Recipes:", data.get('international_count'))
    print("Cache Enabled:", data.get('cache_enabled'))
    assert res.status_code == 200
    assert data.get('total_recipes') >= 10000

    print("\n--- Test 2: 'Almost There' Filter (max_missing=2) ---")
    payload = {
        "ingredients": ["chicken", "rice", "tomato", "garlic", "onion"],
        "max_missing": 2,
        "limit": 5
    }
    res = client.post('/api/recommend-recipes', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    print(f"Found {data['count']} recipes missing at most 2 ingredients:")
    for r in data['results']:
        print(f"  - {r['name']} ({r['cuisine']}) -> Missing ({len(r['missing_ingredients'])}): {r['missing_ingredients']}")
        assert len(r['missing_ingredients']) <= 2

    print("\n--- Test 3: 'More Like This' (Similar Recipes) ---")
    test_recipe = "Mexican Salsa Chicken With Italian Cream Cheese Recipe"
    res = client.get(f'/api/similar-recipes?name={test_recipe}&limit=3')
    assert res.status_code == 200
    data = res.get_json()
    print(f"Similar recipes for '{test_recipe}':")
    for s in data['similar_recipes']:
        print(f"  - {s['name']} (Cuisine: {s['cuisine']}, Sim: {s['similarity']})")
    assert len(data['similar_recipes']) > 0

    print("\n--- Test 4: Cache Loading Performance ---")
    t0 = time.time()
    from app_cosine_similarity import load_data_and_model
    df, vec, mat = load_data_and_model()
    elapsed = time.time() - t0
    print(f"Cache reload took: {elapsed:.3f} seconds (Target: < 0.5s)")
    assert elapsed < 1.0

    print("\n[SUCCESS] ALL ADVANCED BACKEND TESTS PASSED!")

if __name__ == '__main__':
    run_advanced_tests()
