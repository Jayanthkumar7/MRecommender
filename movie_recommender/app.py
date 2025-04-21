from flask import Flask, request, jsonify,render_template
from recommender import recommend
from flask_cors import CORS
import os



app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST','GET'])
def recommend_route():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    data = request.json
    title = data.get('movie_name')
    recommendations = recommend(title)
    if recommendations:
        print(recommendations)  
        return jsonify({'recommendations': recommendations,'ok':True}), 200
    else:
        return jsonify({'error': 'Movie not found'}), 404
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)