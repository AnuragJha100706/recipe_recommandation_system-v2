import sys
import io
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app_cosine_similarity import app

def run_tests():
    client = app.test_client()
    
    print("\n--- Test 1: GET /api/health ---")
    res = client.get('/api/health')
    print("Status:", res.status_code)
    print("Health response:", res.get_json())
    assert res.status_code == 200
    assert res.get_json()['status'] == 'ok'
    
    print("\n--- Test 2: GET /api/cuisines ---")
    res = client.get('/api/cuisines?origin=indian')
    print("Indian cuisines count:", res.get_json()['count'])
    assert res.status_code == 200
    assert 'North Indian Recipes' in res.get_json()['cuisines']
    
    res = client.get('/api/cuisines?origin=out_of_india')
    print("Out-of-India cuisines count:", res.get_json()['count'])
    assert res.status_code == 200
    assert 'Italian Recipes' in res.get_json()['cuisines']
    
    print("\n--- Test 3: POST /api/recommend-recipes (Validation / Empty) ---")
    res = client.post('/api/recommend-recipes', json={})
    print("Empty status:", res.status_code)
    assert res.status_code == 400
    
    print("\n--- Test 4: POST /api/recommend-recipes (Indian Dish) ---")
    payload = {
        "ingredients": ["chicken", "rice", "tomato", "garam masala"],
        "origin": "indian",
        "limit": 3
    }
    res = client.post('/api/recommend-recipes', json=payload)
    data = res.get_json()
    print("Indian recommendations found:", data['count'])
    for r in data['results']:
        print(f"  - [{r['origin']}] {r['name']} ({r['cuisine']}) -> Match: {r['match_score']}%")
        print(f"    Have: {r['matched_ingredients']}")
        print(f"    Need: {r['missing_ingredients'][:4]}...")
        assert r['origin'] == 'Indian'
    assert data['count'] > 0
    
    print("\n--- Test 5: POST /api/recommend-recipes (Out of India Dish) ---")
    payload = {
        "ingredients": ["pasta", "tomato", "cheese", "garlic"],
        "origin": "out_of_india",
        "limit": 3
    }
    res = client.post('/api/recommend-recipes', json=payload)
    data = res.get_json()
    print("Out-of-India recommendations found:", data['count'])
    for r in data['results']:
        print(f"  - [{r['origin']}] {r['name']} ({r['cuisine']}) -> Match: {r['match_score']}%")
        print(f"    Have: {r['matched_ingredients']}")
        print(f"    Need: {r['missing_ingredients'][:4]}...")
        assert r['origin'] == 'Out of India'
    assert data['count'] > 0

    print("\n--- Test 6: POST /api/recommend-recipes (Dietary: Vegetarian) ---")
    payload = {
        "ingredients": ["paneer", "spinach", "tomato", "onion"],
        "origin": "indian",
        "dietary": ["vegetarian"],
        "limit": 3
    }
    res = client.post('/api/recommend-recipes', json=payload)
    data = res.get_json()
    print("Vegetarian recommendations found:", data['count'])
    for r in data['results']:
        print(f"  - {r['name']} (Cuisine: {r['cuisine']}) -> Match: {r['match_score']}%")
    assert data['count'] > 0

    print("\n[SUCCESS] ALL BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
