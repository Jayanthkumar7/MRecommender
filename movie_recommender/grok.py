import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import difflib
import requests
from flask import Flask, request, jsonify, render_template

# TMDb API key
api_key = '32ecb76df8e83902a35c11b63964069e'

# Flask app
app = Flask(__name__)

# Load and preprocess dataset
movies = pd.read_csv('movies_final.csv')

# Fill missing values
columns_to_fill = ['genres', 'keywords', 'tagline', 'overview', 'cast', 'director']
for col in columns_to_fill:
    movies[col] = movies[col].fillna('')

# Fetch movie details from TMDb to populate missing language and imdb_rating
def fetch_movie_details(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        movie = data['results'][0]
        return {
            'imdb_rating': movie.get('vote_average', 0),
            'language': movie.get('original_language', movies['language'].iloc[0] if not movies['language'].empty else 'en'),
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else "Poster not found"
        }
    return {'imdb_rating': 0, 'language': 'en', 'poster_url': "Movie not found"}

# Populate language and imdb_rating if missing
if 'imdb_rating' not in movies.columns:
    movies['imdb_rating'] = 0
if movies['language'].isna().all() or movies['language'].empty:
    movies['language'] = 'en'

for idx, row in movies.iterrows():
    if movies.at[idx, 'imdb_rating'] == 0 or pd.isna(movies.at[idx, 'language']):
        details = fetch_movie_details(row['title'])
        movies.at[idx, 'imdb_rating'] = details['imdb_rating']
        if pd.isna(movies.at[idx, 'language']):
            movies.at[idx, 'language'] = details['language']

# Combine text features
movies['text_features'] = (
    movies['genres'] + ' ' +
    movies['keywords'] + ' ' +
    movies['tagline'] + ' ' +
    movies['overview'] + ' ' +
    movies['cast'] + ' ' +
    movies['director']
)

# Vectorize text features
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(movies['text_features'])

# Normalize numerical feature (imdb_rating)
scaler = MinMaxScaler()
numerical_matrix = scaler.fit_transform(movies[['imdb_rating']])

# One-hot encode language
language_encoded = pd.get_dummies(movies['language'], prefix='lang').values
all_languages = list(pd.get_dummies(movies['language']).columns)

# Combine all features
feature_matrix = np.hstack([tfidf_matrix.toarray(), numerical_matrix, language_encoded])

# Create input vector for virtual profile
def create_input_vector(input_data, vectorizer, scaler, all_languages):
    text_input = []
    if input_data.get('genre'):
        text_input.append(input_data['genre'])
    if input_data.get('actor'):
        text_input.append(input_data['actor'])  # Matches 'cast' column
    if input_data.get('mood'):
        text_input.append(input_data['mood'])
    text_combined = ' '.join(text_input) if text_input else ' '
    text_vector = vectorizer.transform([text_combined]).toarray()
    
    rating = float(input_data.get('rating', 0))
    numerical_vector = scaler.transform([[rating]])
    
    language = input_data.get('language', 'en')
    language_vector = np.zeros(len(all_languages))
    if language in all_languages:
        language_vector[all_languages.index(language)] = 1
    
    return np.hstack([text_vector, numerical_vector, [language_vector]])

# Recommend function
def recommend(input_data, movies, feature_matrix, vectorizer, scaler, all_languages, top_n=10):
    movie_name = input_data.get('movie_name', '').strip()
    if movie_name:
        close_matches = difflib.get_close_matches(movie_name, movies['title'].tolist(), n=1, cutoff=0.6)
        if close_matches:
            movie_name = close_matches[0]
            movie_index = movies[movies['title'] == movie_name].index[0]
            input_vector = feature_matrix[movie_index].reshape(1, -1)
        else:
            input_vector = create_input_vector(input_data, vectorizer, scaler, all_languages)
    else:
        input_vector = create_input_vector(input_data, vectorizer, scaler, all_languages)
    
    similarities = cosine_similarity(input_vector, feature_matrix).flatten()
    top_indices = similarities.argsort()[-top_n:][::-1]
    recommendations = movies.iloc[top_indices][['title', 'genres', 'cast', 'language', 'imdb_rating']]
    
    if input_data.get('rating'):
        recommendations = recommendations[recommendations['imdb_rating'] >= float(input_data['rating'])]
    if input_data.get('language'):
        recommendations = recommendations[recommendations['language'] == input_data['language']]
    
    result = []
    for _, row in recommendations.iterrows():
        poster = fetch_movie_details(row['title'])['poster_url']
        result.append({
            'title': row['title'],
            'genres': row['genres'],
            'cast': row['cast'],
            'language': row['language'],
            'imdb_rating': row['imdb_rating'],
            'poster_url': poster
        })
    
    return result

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    input_data = request.form.to_dict()
    recommendations = recommend(
        input_data, movies, feature_matrix, vectorizer, scaler, all_languages, top_n=10
    )
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True , port=8000)