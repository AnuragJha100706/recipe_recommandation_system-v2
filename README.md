# Recipe Recommender Web App

This is a web application that recommends recipes based on input ingredients. Users can enter a list of ingredients they have, and the app will provide a list of recommended recipes.

## Features

- **Input Ingredients:** Users can enter a list of ingredients.
- **Recipe Recommendations:** The app provides a list of recommended recipes based on the input ingredients.
- **Recipe Details:** Users can view details of each recommended recipe, including ingredients and instructions.

## Data Collection

The recipe data for this application was collected using a web scraping script written in Python using BeautifulSoup. The script extracted recipes from [your-source] and saved them in a structured format.

## Server Apps

The application uses two server apps for recipe recommendations:

- **app_neural_network.py:** Uses neural networks for recipe recommendations.
- **app_cosine_similarity.py:** Uses cosine similarity for recipe recommendations.

## Technologies Used

- React: Frontend framework for building the user interface.
- Flask: Backend framework for handling recipe recommendations.
- TensorFlow: Used for the recipe recommendation model.
- NLTK: Natural Language Toolkit for text processing.

## Getting Started

### Prerequisites

- Node.js
- Python: Install Python to run the Flask backend.
- TensorFlow
- NLTK

### Usage

1. Start the Flask backend:

    - For neural network server:

        ```bash
        cd server
        python app_neural_network.py
        ```

    - For cosine similarity server:

        ```bash
        cd server
        python app_cosine_similarity.py
        ```

2. Start the React frontend:

    ```bash
    cd client
    npm start
    ```

3. Open your browser and visit `http://localhost:3000` to use the application.

![capture](capture_website.png)

