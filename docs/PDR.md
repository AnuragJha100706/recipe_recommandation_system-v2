# Product Design Requirements Document

## 1. Product Overview

**Product name:** Smart Recipe Recommender

**Purpose:**  
Help users discover recipes based on the ingredients they already have, while considering cooking time, cuisine, origin (Indian dishes vs. Out-of-India / International dishes), dietary preferences, and ingredient availability.

**Current implementation:**
- Flask backend (`server/app_cosine_similarity.py`)
- TF-IDF and cosine similarity recommendation engine
- CSV-based recipe dataset (`server/recipes_3.csv` with 5,938 total recipes)
- Standalone HTML/CSS/JavaScript frontend (`client/recipe_recommender.html`)
- Optional, currently unused LSTM model (`server/train_model.py`)

Primary files:
- `server/app_cosine_similarity.py`
- `server/recipes_3.csv`
- `client/recipe_recommender.html`
- `server/train_model.py`
- `server/expand_international_dataset.py` *(New dataset pipeline tool)*

---

## 2. Problem Statement

Users often have ingredients available but do not know what to cook. Existing recipe websites typically require users to search for a specific recipe instead of starting with their available ingredients.

Furthermore, users often have a clear culinary mood:
- *“I want to make an authentic Indian dish (dal, curry, biryani, sabzi, etc.).”*
- *“I want to make something out of India / international (Italian pasta, Mexican tacos, Asian noodles, Continental soup, etc.).”*

The product should answer:
> “What can I cook with what I already have, in the culinary style (Indian or Out-of-India) that I want?”

It should also explain:
- Why a recipe was recommended
- Which ingredients are already available
- Which ingredients are missing
- Whether it is an Indian dish or Out-of-India (International) dish
- How long the recipe takes
- What regional cuisine or dietary category it belongs to

---

## 3. Product Goals

### Primary goals
1. Recommend relevant recipes from user-provided ingredients.
2. Support distinct options for **Indian dishes** vs. **Out-of-India (Global / International) dishes**, plus specific sub-cuisines.
3. Support filters for time, cuisine, ingredient count, and dietary exclusions.
4. Show explainable recommendation results (matched ingredients, missing ingredients, match percentage).
5. Provide a fast, responsive, accessible culinary interface.
6. Use real recipe images and source links.
7. Provide a robust dataset covering both rich Indian regional cuisine and diverse out-of-India international cuisine.
8. Establish a measurable recommendation baseline.
9. Create a foundation for future personalization.

### Secondary goals
- Reduce food waste.
- Help users plan meals.
- Generate shopping lists from missing ingredients.
- Support future favorites, ratings, and pantry management.

### Non-goals for the first release
- User authentication
- Payments
- Social features
- Fully conversational AI
- Cloud-scale infrastructure
- Replacing TF-IDF before measuring its performance
- Treating the current LSTM classifier as the primary recommender

---

## 4. Target Users

### Casual home cook
Wants quick ideas from ingredients currently in their pantry.

### Indian cuisine lover
Wants authentic Indian regional recipes (North Indian, South Indian, Bengali, Punjabi, Maharashtrian, Chettinad, etc.) matching their spices and pantry staples.

### Global / International food lover ("Out-of-India" dishes)
Wants Continental, Italian, Mexican, Chinese, Thai, Mediterranean, French, Japanese, or American dishes.

### Busy professional or student
Needs recipes filtered by a short preparation or cooking time (<30 mins).

### Dietary-conscious user
Needs vegetarian, vegan, gluten-free, or ingredient-exclusion options.

### Food planner
Wants to save recipes, create a shopping list, and plan future meals.

---

## 5. User Stories

- As a user, I want to enter several ingredients and receive recipe suggestions.
- As a user, I want to choose between **All Dishes**, **Indian Dishes**, and **Out-of-India Dishes**.
- As a user, I want to filter by specific cuisines under my chosen category (e.g. Italian/Mexican under Out-of-India, or Punjabi/Kerala under Indian).
- As a user, I want to see how closely each recipe matches my ingredients.
- As a user, I want to know which ingredients are missing.
- As a user, I want to set a maximum cooking time.
- As a user, I want to avoid ingredients I cannot or do not want to eat.
- As a user, I want to view complete cooking instructions.
- As a user, I want to open the original recipe source.
- As a user, I want to add missing ingredients to a shopping list.
- As a user, I want the application to work well on mobile and desktop.
- As a user, I want useful feedback when no recipes or an error occurs.

---

## 6. Release Strategy

### MVP: Explainable Recipe Discovery (Milestones 1 & 2)
- Ingredient search with chips
- TF-IDF recommendation engine
- **Dish Origin selector (All / Indian Dishes / Out-of-India Dishes)**
- Cascading cuisine filter
- Maximum cooking-time filter
- Maximum ingredient-count filter
- Match percentage
- Matched ingredients (Have) & Missing ingredients (Need)
- Real recipe image with fallback
- Recipe source URL
- Responsive UI
- Loading, error, and no-results states
- Shopping list drawer (`localStorage`)

### Version 1.5: Personal Utility
- Favorites
- Ratings
- Pantry list
- Shopping-list persistence
- Serving-size adjustment
- Print-friendly recipe view
- SQLite storage

### Version 2: Intelligent Personalization
- User history
- Personalized ranking
- Semantic embeddings (Sentence-Transformers)
- Hybrid recommendation model
- Similar-recipe recommendations
- Natural-language search

---

## 7. Functional Requirements

### FR-01: Ingredient input
The system shall allow users to enter multiple ingredients separated by commas or entered as interactive chips.

### FR-02: Ingredient normalization
The backend shall normalize uppercase/lowercase text, punctuation, extra spaces, common singular/plural forms, and basic aliases.

### FR-03: Recipe recommendation
The backend shall rank recipes according to ingredient similarity using TF-IDF and cosine similarity.

### FR-04: Dish origin & recipe filters
The system shall support:
- **Dish Origin**:
  - `all`: Search across all recipes.
  - `indian`: Only return Indian regional recipes.
  - `out_of_india` (or `international`): Only return recipes from outside India.
- **Cuisine**: Cascading options matching the chosen origin.
- **Maximum cooking time**: Numerical filter in minutes.
- **Maximum ingredient count**: Numerical filter.
- **Dietary preference or exclusions**: Conservative exclusions (vegetarian, vegan, gluten-free).
- **Number of results**: Limit parameter (default 10, max 50).

### FR-05: Explainable results
Each result shall include:
- Recipe title
- Match score (%)
- Matched ingredients
- Missing ingredients
- Dish origin (`Indian` or `Out of India`)
- Cuisine
- Cooking time
- Ingredient count
- Ingredient list
- Instructions
- Image URL
- Original recipe URL

### FR-06: Recipe details
Users shall be able to expand recipes in a modal, read ingredients and step-by-step instructions, and open the original source.

### FR-07: Shopping list
Users shall be able to add missing ingredients to a temporary shopping list stored in `localStorage`.

### FR-08: Error handling
Show understandable messages for empty input, invalid requests, server unavailability, and empty results.

---

## 8. Dataset Strategy: Indian vs. Out-of-India Dishes

### 8.1 Existing Dataset Analysis (`recipes_3.csv` & `recipes_expanded.csv`)
The baseline dataset contains **5,938 recipes** and has now been expanded to **6,728 complete recipes** (via `server/expand_international_dataset.py`):
- **Indian Dishes (3,970 recipes)**:
  - Covers 40+ regional cuisines: North Indian (763), South Indian (558), Maharashtrian (152), Bengali (150), Karnataka (138), Tamil Nadu (133), Kerala (133), Andhra (109), Rajasthani (99), Gujarati (96), Goan (85), Chettinad (65), Punjabi (61), Kashmiri (44), Mangalorean (45), Parsi (36), Awadhi (33), Mughlai (25), Bihari (25), Assamese (28), Hyderabadi (26), Udupi (15), etc.
- **Out-of-India / International Dishes (2,758 recipes)**:
  - Expanded from 1,968 baseline recipes with 790 authentic global dishes from TheMealDB.
  - Covers Continental (952), Italian (450+), Mexican (230+), British, American, French, Chinese, Japanese, Asian, Thai, Middle Eastern, Mediterranean, European, African, Greek, etc.

### 8.2 Dataset Tagging & Expansion Pipeline
1. **Origin Classification Layer**:
   - Explicitly classify each recipe into `origin`: `"Indian"` or `"International"` based on mapped cuisine metadata.
   - Clean whitespace and special characters (e.g. remove trailing `\ufeff` from `Gujarati Recipes\ufeff`).
2. **Out-of-India Expansion (`server/expand_international_dataset.py`)**:
   - Automated ingestion script using **TheMealDB open API** and/or curated open international food datasets.
   - Fetches hundreds of additional verified recipes from Italian, Mexican, French, American, Japanese, British, Greek, and Canadian culinary traditions.
   - Normalizes them into the 9 standardized columns (`TranslatedRecipeName`, `TranslatedIngredients`, `TotalTimeInMins`, `Cuisine`, `TranslatedInstructions`, `URL`, `Cleaned-Ingredients`, `image-url`, `Ingredient-count`).
   - Merges seamlessly into the primary dataset without breaking schema consistency.

---

## 9. Recommendation Design

### Initial scoring model
```text
final_score =
  0.60 * ingredient_similarity
+ 0.15 * ingredient_coverage
+ 0.10 * cuisine_match
+ 0.10 * cooking_time_match
+ 0.05 * popularity_or_quality
```

### Ingredient coverage
```text
ingredient_coverage = matched_user_ingredients / total_required_ingredients
```

### Missing ingredients
Compare normalized user ingredients with normalized recipe ingredients and return ingredients not found in user input.

### Dietary filtering
Conservative ingredient exclusions clearly marked as approximate:
- Vegan: meat, fish, egg, milk, butter, cheese
- Vegetarian: meat and fish
- Gluten-free: wheat, flour, barley, rye, bread

---

## 10. API Requirements

### Health endpoint
```http
GET /api/health
```
Example response:
```json
{
  "status": "ok",
  "recipe_count": 5938,
  "indian_count": 3970,
  "international_count": 1968
}
```

### Recommendation endpoint
```http
POST /api/recommend-recipes
Content-Type: application/json
```

Request:
```json
{
  "ingredients": ["chicken", "rice", "tomato"],
  "origin": "out_of_india",
  "cuisine": "Mexican",
  "max_time": 45,
  "max_ingredients": 12,
  "dietary": [],
  "limit": 10
}
```

Response:
```json
{
  "results": [
    {
      "name": "Mexican Chicken and Rice",
      "origin": "Out of India",
      "match_score": 88,
      "matched_ingredients": ["chicken", "rice", "tomato"],
      "missing_ingredients": ["garlic", "cilantro", "lime"],
      "ingredients": ["chicken", "rice", "tomato", "garlic", "cilantro", "lime"],
      "instructions": ["Sear chicken", "Cook rice with tomatoes and garlic", "Garnish with cilantro and lime"],
      "cuisine": "Mexican",
      "total_time_minutes": 35,
      "ingredient_count": 6,
      "image_url": "https://example.com/image.jpg",
      "source_url": "https://example.com/recipe"
    }
  ],
  "count": 1
}
```

### Cuisines endpoint *(New)*
```http
GET /api/cuisines?origin=all|indian|out_of_india
```
Returns available cuisines grouped or filtered by origin to populate frontend dropdowns dynamically.

---

## 11. UI Requirements

### Origin selector
Prominent segmented control or toggle pills at the top of the search interface:
- 🍽️ **All Dishes**
- 🇮🇳 **Indian Dishes** (Curries, Dals, Biryanis, Dosas, Thalis)
- 🌍 **Out of India Dishes** (Continental, Italian, Mexican, Asian, etc.)

When clicked:
- Dynamically filters results
- Updates the Cuisine filter dropdown with relevant regional sub-cuisines

### Card metadata badges
- Origin badge: `🇮🇳 Indian` or `🌍 Out of India`
- Cuisine badge (e.g. `Italian`, `South Indian`, `Mexican`)
- Cooking time badge
- Match score badge

---

## 12. Main Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---:|---|
| Imbalance between Indian and non-Indian recipes | Medium | Use `expand_international_dataset.py` to ingest 300-1000+ extra global dishes from TheMealDB |
| Misclassified cuisines | Low | Maintain curated mapping set of all Indian vs Out-of-India cuisine strings |
| Image URL deadlinks | Medium | Implement client-side image error fallback to high-quality cuisine placeholders |
| Large dataset search latency | Low | Vectorize once at startup; filter candidates in memory using Pandas vectorized masks |
