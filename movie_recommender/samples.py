import requests
import pandas as pd
import time

api_key = '32ecb76df8e83902a35c11b63964069e'

movie_data = []
count = 1
print("hello world !")
for page in range(1, 301):  
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_original_language=te&language=en-US&sort_by=popularity.desc&page={page}"
    response = requests.get(url).json()
    
    for movie in response.get('results', []):
        movie_id = movie['id']
        title = movie.get('title')
        overview = movie.get('overview')
        language = movie.get('original_language')
        
        # Fetch full movie details (including genres, tagline, etc.)
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=credits"
        details = requests.get(details_url).json()
        
        genres = " ".join([g['name'] for g in details.get('genres', [])])
        tagline = details.get('tagline', '')
        keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={api_key}"
        keywords_data = requests.get(keywords_url).json()
        keywords = " ".join([k['name'] for k in keywords_data.get('keywords', [])])
        
        cast = details.get('credits', {}).get('cast', [])[:5]
        cast_names = " ".join([c['name'] for c in cast])
        
        crew = details.get('credits', {}).get('crew', [])
        director = next((c['name'] for c in crew if c['job'] == 'Director'), '')
        
        movie_data.append({
            'id': count,
            'title': title,
            'genres': genres,
            'keywords': keywords,
            'tagline': tagline,
            'overview': overview,
            'cast': cast_names,
            'director': director,
            'language': language
        })
        count += 1
        
    print(f"Fetched page {page}")
    time.sleep(0.25)  # to avoid hitting rate limits

# Save to CSV
df = pd.DataFrame(movie_data)
df.to_csv('expanded_movies_3.csv', index=False)
print("Saved 10,000+ movies!")
