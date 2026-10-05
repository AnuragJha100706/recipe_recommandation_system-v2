# Smart Recipe Recommender - Project Implementation Roadmap & TODO List

Based on the updated [Product Design Requirements (PDR)](file:///j:/My%20Drive/projects/COMPLETE%20PROJECT/Machine%20learning%20project/docs/PDR.md).

---

## 🎯 Recommended Immediate Focus: Milestones 1 & 2 Together
*(Transform the core engine and standalone client into an explainable, modern food discovery application with dedicated Indian & Out-of-India dish options)*

---

## 📋 Milestone 1: Backend Foundation (API, Origin Tagging & Recommendation Engine)

- [x] **Data Pipeline, Origin Classification & Preprocessing (`server/`)**
  - [x] Inspect existing `recipes_3.csv` (contains 5,938 recipes: 3,970 Indian, 1,968 Out-of-India).
  - [x] Implement Origin Classification:
    - [x] Map 40+ Indian regional cuisines to `Indian` (`North Indian`, `South Indian`, `Bengali`, `Punjabi`, `Mughlai`, `Kerala`, etc.).
    - [x] Map 20+ global cuisines to `Out of India` (`Continental`, `Italian`, `Mexican`, `Asian`, `Chinese`, `Thai`, `French`, `Japanese`, etc.).
    - [x] Clean encoding artifacts (e.g. `\ufeff` in `Gujarati Recipes`).
  - [x] Build Out-of-India dataset ingestion script (`server/expand_international_dataset.py`):
    - [x] Fetch additional international recipes from TheMealDB open API across global cuisines.
    - [x] Map fields to unified 9-column CSV schema.
    - [x] Merge and enrich dataset with verified international dishes (Total: 6,728 recipes in `recipes_expanded.csv`).
  - [x] Build robust ingredient normalization module:
    - [x] Lowercasing, punctuation stripping, extra whitespace removal.
    - [x] Lemmatization / stemming for singular & plural unification (e.g., `tomatoes` -> `tomato`).
    - [x] Common alias / modifier stripping (e.g., `chicken breast` -> `chicken`, `red onions` -> `onion`).
  - [x] Cache TF-IDF vectorizer and precomputed ingredient matrix in memory on startup.

- [x] **Recommendation Algorithm Upgrade (`server/app_cosine_similarity.py`)**
  - [x] Multi-factor scoring formula:
    $$\text{Score} = 0.60 \times \text{Similarity} + 0.25 \times \text{Coverage} + 0.10 \times \text{Cuisine} + 0.05 \times \text{Time}$$
  - [x] Calculate **matched ingredients** and **missing ingredients** for each candidate recipe.
  - [x] Compute **ingredient coverage percentage**: $\frac{\text{matched user ingredients}}{\text{total required ingredients}}$.

- [x] **Origin Filtering & Query Parameters**
  - [x] **Dish Origin filter**: `origin = "all" | "indian" | "out_of_india"`.
  - [x] Filter by `cuisine` (cascaded by origin or standalone).
  - [x] Filter by `max_time` (<= total minutes).
  - [x] Filter by `max_ingredients` (<= ingredient count).
  - [x] Filter by `dietary` exclusions (vegan, vegetarian, gluten-free heuristic keywords).
  - [x] Configurable `limit` parameter (default: 12, max: 50).

- [x] **API Contracts & Endpoints**
  - [x] Implement `GET /api/health` returning `{ "status": "ok", "recipe_count": N, "indian_count": N, "international_count": N }`.
  - [x] Implement `GET /api/cuisines?origin=all|indian|out_of_india` for cascading UI dropdowns.
  - [x] Refactor `POST /api/recommend-recipes`:
    - [x] Accept JSON: `{ "ingredients": [...], "origin": "all"|"indian"|"out_of_india", "cuisine": "...", "max_time": 45, ... }`.
    - [x] Standardize response schema: `{ "results": [...], "count": N }`.
    - [x] Include origin metadata (`origin`: `Indian` | `Out of India`) and explainability badges in each result.
  - [x] Robust error handling & validation (400 for empty/invalid input, 500 fallback).

---

## 🎨 Milestone 2: Modern UI & UX (`client/recipe_recommender.html`)

- [x] **Visual Design & Culinary Theme**
  - [x] Warm neutral aesthetic (`#faf7f2`, `#2d3748`, fresh herb green `#2e7d32`, terracotta `#c85a32`).
  - [x] Clean typography using Google Fonts (Inter / Outfit).
  - [x] Mobile & desktop responsive layout.

- [x] **Origin Selector Control**
  - [x] Prominent segmented tabs / pill toggle at the top of the search section:
    - 🍽️ **All Dishes**
    - 🇮🇳 **Indian Dishes**
    - 🌍 **Out of India Dishes**
  - [x] Switching origin immediately updates search context and dynamically cascades the Cuisine dropdown options.

- [x] **Interactive Ingredient Input**
  - [x] Tag/chip input with Enter / comma key support and click-to-remove.
  - [x] Context-aware quick-add popular ingredient pills (e.g., Paneer, Garam Masala, Chicken, Pasta, Cheese, Rice, Garlic).
  - [x] "Clear all" button.

- [x] **Filter Controls Toolbar**
  - [x] Dynamic Cuisine dropdown (showing Indian regional cuisines or International cuisines depending on Origin selector).
  - [x] Max cooking time slider / quick buttons (15m, 30m, 45m, 60m+).
  - [x] Max ingredient count selector.
  - [x] Dietary exclusion toggles (Vegetarian, Vegan, Gluten-Free).
  - [x] Result limit selector.

- [x] **Explainable Recipe Cards**
  - [x] Origin badge: `🇮🇳 Indian` or `🌍 Out of India`.
  - [x] Real recipe image from `image_url` with reliable culinary fallback.
  - [x] Match percentage badge (color-coded: green >= 75%, amber >= 50%, gray < 50%).
  - [x] Cuisine tag, cooking time badge, ingredient count badge.
  - [x] Visual breakdown of **Have** (matched ingredients in green) vs **Need** (missing ingredients in amber).
  - [x] "View Full Recipe" action and "Add Missing to Shopping List" action.

- [x] **Recipe Detail Modal / Drawer**
  - [x] Modal dialog showing recipe image, origin, cuisine, cooking time, full ingredients, and step-by-step instructions.
  - [x] Safe DOM rendering to prevent XSS (no raw `innerHTML` for scraped text).
  - [x] External link to original recipe source URL.

- [x] **Shopping List Drawer**
  - [x] Slide-out drawer or overlay for shopping list.
  - [x] One-click add missing ingredients from any recipe card.
  - [x] Check off items as bought; remove items; "Clear list" action.
  - [x] Persist shopping list in browser `localStorage`.

- [x] **State Feedback**
  - [x] Loading skeleton cards / culinary spinner during search.
  - [x] Clean empty state on first visit.
  - [x] Friendly no-results state with suggestions to loosen filters or switch origin.
  - [x] Network / server error alert with retry button.

---

## 🧪 Milestone 3: Quality, Testing & Security

- [ ] **Backend Tests (`server/tests/`)**
  - [ ] Unit tests for origin classification (verify Indian vs Out-of-India cuisine tags).
  - [ ] Tests for ingredient normalization and alias resolution.
  - [ ] API integration tests: valid search, empty input, invalid filters, edge cases.
- [ ] **Frontend Verification & Accessibility**
  - [ ] Origin switch interaction testing.
  - [ ] ARIA labels for buttons, inputs, and modal accessibility.
  - [ ] Keyboard navigation support (Esc to close modal/drawer).
- [ ] **Security & Hardening**
  - [ ] DOM-safe element creation.
  - [ ] CORS configuration.
- [ ] **Recommendation Quality Baseline**
  - [ ] Curate 20 standard ingredient benchmarks (10 Indian queries, 10 Out-of-India queries).
  - [ ] Record baseline metrics (Precision@5, Precision@10, response latency < 500ms).

---

## 🚀 Milestone 4: Personal Utility & Convenience (Completed)

- [x] **Favorites / Bookmarking System**:
  - [x] Heart toggle button on every card and inside recipe modal.
  - [x] Header favorites button with live badge counter.
  - [x] Saved favorites slide-over drawer with item removal and direct recipe opening.
  - [x] Persists in browser `localStorage`.
- [x] **"Almost There" (Missing $\le 2$ Items) Smart Filter**:
  - [x] Backend parameter `max_missing` filtering candidates by missing ingredient count.
  - [x] Filter button toggle in UI toolbar.
  - [x] Prominent card banner: `⚡ Just need: [Missing Items]`.
- [x] **Pantry Staples Memory ("My Kitchen")**:
  - [x] Expandable pantry staples tray with 10 standard staples (Salt, Oil, Garlic, Onion, Flour, Butter, etc.).
  - [x] Automatically merged into active query without cluttering user input chips.
  - [x] Persists in `localStorage`.
- [x] **Dynamic Serving Size Scaler**:
  - [x] `[-] 2 Servings [+]` stepper in recipe modal.
  - [x] Dynamic numeric and fraction scaler in JavaScript updating ingredient quantities in real time.
- [x] **Print-Friendly Recipe View**:
  - [x] `🖨️ Print` button in modal.
  - [x] Custom `@media print` CSS rules formatting recipe into a clean 1-page document.
- [x] **"More Like This" (Similar Recipes Engine)**:
  - [x] Dedicated endpoint `GET /api/similar-recipes?name=...&limit=3`.
  - [x] Embedded interactive cards at the bottom of the recipe modal.
- [x] **Sub-Second Startup (Disk Caching)**:
  - [x] Model and matrix serialized to `server/cache/recommender_cache.joblib`.
  - [x] Backend startup drops from 4s to **0.78 seconds**!
- [x] **1-Click Launchers**:
  - [x] Created `run_app.py` and `start_app.bat` for instant double-click launching.

---

## 🧠 Milestone 5: Advanced Intelligence & Scaling (Food.com Ingestion Completed)

- [x] **Food.com Dataset Ingestion (231k corpus)**:
  - [x] Filtered and curated 3,500 premium international dishes from `recipes/RAW_recipes.csv`.
  - [x] Scaled corpus to **10,228 total recipes** (3,970 Indian, 6,258 International).
- [ ] Semantic embeddings integration (Sentence-Transformers / all-MiniLM-L6-v2).
- [ ] Hybrid ranking: dense vector similarity + lexical TF-IDF matching.
- [ ] Conversational recipe query parser.
