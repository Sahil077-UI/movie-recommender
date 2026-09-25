from flask import Flask, render_template, jsonify, request
import pandas as pd
import pickle
import requests
import os

from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)


# -----------------------------
# Load environment variables
# -----------------------------

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")


# -----------------------------
# Load recommendation model
# -----------------------------

df = pd.read_pickle("models/df.pkl")

indices = pickle.load(
    open("models/indices.pkl", "rb")
)

genre_matrix = pickle.load(
    open("models/genre_matrix.pkl", "rb")
)

overview_matrix = pickle.load(
    open("models/overview_matrix.pkl", "rb")
)

tagline_matrix = pickle.load(
    open("models/tagline_matrix.pkl", "rb")
)


# -----------------------------
# Title lookup
# -----------------------------

title_lookup = {
    str(title).strip().lower(): title
    for title in indices.index
}


# -----------------------------
# Recommendation function
# -----------------------------

def recommend(title, n=10):

    title = " ".join(
        title.strip().lower().split()
    )

    if title not in title_lookup:
        return []

    actual_title = title_lookup[title]

    idx = indices[actual_title]

    genre_similarity = cosine_similarity(
        genre_matrix[idx],
        genre_matrix
    ).flatten()

    overview_similarity = cosine_similarity(
        overview_matrix[idx],
        overview_matrix
    ).flatten()

    tagline_similarity = cosine_similarity(
        tagline_matrix[idx],
        tagline_matrix
    ).flatten()

    final_score = (
        0.55 * genre_similarity +
        0.40 * overview_similarity +
        0.05 * tagline_similarity
    )

    # Don't recommend the movie itself
    final_score[idx] = -1

    similar_idx = final_score.argsort()[::-1][:n]

    return df["title"].iloc[similar_idx].tolist()


# -----------------------------
# TMDB movie details
# -----------------------------

def get_movie_details(title):

    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "include_adult": False
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.RequestException as e:

        print(f"TMDB error for {title}: {e}")

        return {
            "title": title,
            "overview": "",
            "rating": None,
            "release_date": "",
            "poster": None
        }

    results = data.get("results", [])

    if not results:

        return {
            "title": title,
            "overview": "",
            "rating": None,
            "release_date": "",
            "poster": None
        }

    # Try to find exact title
    movie = None

    for result in results:

        tmdb_title = result.get("title", "")

        if tmdb_title.strip().lower() == title.strip().lower():

            movie = result
            break

    # Otherwise use first result
    if movie is None:
        movie = results[0]

    poster_path = movie.get("poster_path")

    poster_url = None

    if poster_path:

        poster_url = (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    return {
        "title": movie.get("title", title),
        "overview": movie.get("overview", ""),
        "rating": movie.get("vote_average"),
        "release_date": movie.get("release_date", ""),
        "poster": poster_url
    }


# -----------------------------
# Home page
# -----------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# Recommendation API
# -----------------------------

@app.route("/recommend")
def get_recommendations():

    title = request.args.get(
        "title",
        ""
    )

    if not title.strip():

        return jsonify({
            "error": "Please enter a movie title."
        }), 400

    recommendations = recommend(title)

    if not recommendations:

        return jsonify({
            "error": "Movie not found."
        }), 404

    movies = []

    for movie_title in recommendations:

        details = get_movie_details(
            movie_title
        )

        movies.append(details)

    return jsonify({
        "movie": title,
        "recommendations": movies
    })


# -----------------------------
# Run application
# -----------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )