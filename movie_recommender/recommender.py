import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import difflib
import requests


api_key = '32ecb76df8e83902a35c11b63964069e'


movies = pd.read_csv('movies_final.csv')
list_of_values = ['genres', 'keywords', 'tagline', 'cast', 'director','overview']
for i in list_of_values:
    movies[i] = movies[i].fillna('')
movies_combined = movies['genres']+' ' + movies['keywords']+' ' + movies['tagline']+' ' + movies['cast']+' ' + movies['director']+ ' ' + movies['overview']
movies_combined = movies_combined.apply(lambda x: x.lower())


vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(movies_combined)
similarity = cosine_similarity(tfidf_matrix)



# get movie details from the API
def get_movie_details(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0]['poster_path']
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return poster_url
        return "Poster not found"
    return "Movie not found"

def recommend(name):
    try:
        name = difflib.get_close_matches(name, movies['title'].tolist())
        name = name[0]
        movie_index = movies[movies['title'] == name].index[0]
        
    except IndexError:
        print("Movie not found!")
        return
    similarity_score = list(enumerate(similarity[movie_index]))
    similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)
    similarity_movies = similarity_score[1:6]
    recommended_movies = [] 
    for i in similarity_movies:
        recommended_movies.append(movies.iloc[i[0]]['title'])
    recommendations = []
    for i in recommended_movies:
        poster = get_movie_details(i)
        recommendations.append([i,poster])
    return recommendations
        

if __name__ == "__main__":
    
    recommend(input("Enter movie name: "))