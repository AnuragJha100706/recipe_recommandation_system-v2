import pandas as pd
import numpy as np
import nltk
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, GlobalMaxPool1D
import pickle

# Load data
print("Loading data...")
df = pd.read_csv('server/recipes_3.csv')

# Preprocess ingredients
print("Preprocessing ingredients...")
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(nltk.corpus.stopwords.words('english'))
def preprocess_text(text):
    # If ingredients are a list in string form, join them
    if isinstance(text, str) and text.startswith('['):
        try:
            import ast
            text = ' '.join(ast.literal_eval(text))
        except:
            pass
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
    return ' '.join(words)
df['Processed_Ingredients'] = df['Cleaned-Ingredients'].apply(preprocess_text)

# Tokenize
print("Tokenizing...")
max_words = 5000
max_len = 50
tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(df['Processed_Ingredients'])
sequences = tokenizer.texts_to_sequences(df['Processed_Ingredients'])
X = pad_sequences(sequences, maxlen=max_len)

# Encode labels
print("Encoding labels...")
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['TranslatedRecipeName'])
y = to_categorical(y)

# Build model
print("Building model...")
model = Sequential([
    Embedding(max_words, 128, input_length=max_len),
    LSTM(64, return_sequences=True),
    GlobalMaxPool1D(),
    Dense(64, activation='relu'),
    Dense(y.shape[1], activation='softmax')
])
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train
print("Training model...")
model.fit(X, y, epochs=10, batch_size=32, validation_split=0.1)

# Save model and preprocessors
print("Saving model and preprocessors...")
model.save('recipe_recommendation_model.h5')
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open('label_encoder.pickle', 'wb') as handle:
    pickle.dump(label_encoder, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("Training complete! Model and preprocessors saved.")
