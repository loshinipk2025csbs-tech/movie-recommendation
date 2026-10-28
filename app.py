import os
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get("MOVIE_DB_PATH", str(BASE_DIR / "movies.db"))
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-before-production")

# Small starter catalogue so the project runs immediately without an API key.
# Replace/extend this list with a properly licensed movie dataset for a larger project.
MOVIES = [
    {"id": 1, "title": "Inception", "year": 2010, "genres": ["Sci-Fi", "Action", "Thriller"], "rating": 8.8, "description": "A thief enters dreams to steal secrets and is offered a chance at redemption.", "tags": ["dreams", "heist", "mind-bending", "technology"]},
    {"id": 2, "title": "Interstellar", "year": 2014, "genres": ["Sci-Fi", "Drama", "Adventure"], "rating": 8.7, "description": "Explorers travel through a wormhole to search for a future for humanity.", "tags": ["space", "time", "family", "science"]},
    {"id": 3, "title": "The Dark Knight", "year": 2008, "genres": ["Action", "Crime", "Drama"], "rating": 9.0, "description": "Batman faces a criminal mastermind who plunges Gotham into chaos.", "tags": ["superhero", "crime", "justice", "dark"]},
    {"id": 4, "title": "The Matrix", "year": 1999, "genres": ["Sci-Fi", "Action"], "rating": 8.7, "description": "A hacker discovers reality is a simulation and joins a rebellion.", "tags": ["simulation", "technology", "mind-bending", "future"]},
    {"id": 5, "title": "Toy Story", "year": 1995, "genres": ["Animation", "Comedy", "Family"], "rating": 8.3, "description": "Toys come to life when humans are not around.", "tags": ["friendship", "toys", "family", "fun"]},
    {"id": 6, "title": "Finding Nemo", "year": 2003, "genres": ["Animation", "Adventure", "Family"], "rating": 8.2, "description": "A clownfish crosses the ocean to find his missing son.", "tags": ["ocean", "family", "friendship", "adventure"]},
    {"id": 7, "title": "The Shawshank Redemption", "year": 1994, "genres": ["Drama"], "rating": 9.3, "description": "Two prisoners build a friendship and hold on to hope over many years.", "tags": ["hope", "friendship", "prison", "inspiration"]},
    {"id": 8, "title": "La La Land", "year": 2016, "genres": ["Romance", "Drama", "Music"], "rating": 8.0, "description": "A musician and an aspiring actor fall in love while pursuing their dreams.", "tags": ["music", "love", "dreams", "hollywood"]},
    {"id": 9, "title": "The Grand Budapest Hotel", "year": 2014, "genres": ["Comedy", "Adventure"], "rating": 8.1, "description": "A hotel concierge and his protégé become involved in a theft and family dispute.", "tags": ["hotel", "mystery", "friendship", "quirky"]},
    {"id": 10, "title": "Get Out", "year": 2017, "genres": ["Horror", "Mystery", "Thriller"], "rating": 7.8, "description": "A weekend visit becomes a disturbing mystery for a young photographer.", "tags": ["suspense", "mystery", "social thriller", "secrets"]},
    {"id": 11, "title": "Avengers: Endgame", "year": 2019, "genres": ["Action", "Sci-Fi", "Adventure"], "rating": 8.4, "description": "Heroes unite for a final mission to reverse a devastating loss.", "tags": ["superhero", "teamwork", "space", "technology"]},
    {"id": 12, "title": "Pride and Prejudice", "year": 2005, "genres": ["Romance", "Drama"], "rating": 7.8, "description": "Elizabeth Bennet navigates family expectations and a complicated romance.", "tags": ["love", "family", "period", "relationships"]},
    {"id": 13, "title": "Coco", "year": 2017, "genres": ["Animation", "Family", "Fantasy", "Music"], "rating": 8.4, "description": "A young musician journeys into the Land of the Dead to learn about his family.", "tags": ["music", "family", "memory", "adventure"]},
    {"id": 14, "title": "Jurassic Park", "year": 1993, "genres": ["Adventure", "Sci-Fi", "Thriller"], "rating": 8.2, "description": "A theme park of cloned dinosaurs becomes a fight for survival.", "tags": ["dinosaurs", "science", "survival", "technology"]},
    {"id": 15, "title": "The Conjuring", "year": 2013, "genres": ["Horror", "Mystery"], "rating": 7.5, "description": "Paranormal investigators help a family terrorized by a dark presence.", "tags": ["supernatural", "haunted", "suspense", "family"]},
    {"id": 16, "title": "Whiplash", "year": 2014, "genres": ["Drama", "Music"], "rating": 8.5, "description": "A driven drummer faces an intense instructor at a music conservatory.", "tags": ["music", "ambition", "performance", "discipline"]},
    {"id": 17, "title": "Spider-Man: Into the Spider-Verse", "year": 2018, "genres": ["Animation", "Action", "Adventure", "Sci-Fi"], "rating": 8.4, "description": "A teenager meets heroes from other dimensions and discovers his potential.", "tags": ["superhero", "multiverse", "friendship", "technology"]},
    {"id": 18, "title": "Knives Out", "year": 2019, "genres": ["Mystery", "Comedy", "Crime"], "rating": 7.9, "description": "A detective investigates a novelist's suspicious death in a wealthy family.", "tags": ["detective", "mystery", "family", "investigation"]},
    {"id": 19, "title": "The Lion King", "year": 1994, "genres": ["Animation", "Adventure", "Drama", "Family"], "rating": 8.5, "description": "A young lion learns responsibility and returns to reclaim his home.", "tags": ["animals", "family", "friendship", "coming of age"]},
    {"id": 20, "title": "Dune", "year": 2021, "genres": ["Sci-Fi", "Adventure", "Drama"], "rating": 8.0, "description": "A young noble travels to a dangerous desert planet central to humanity's future.", "tags": ["space", "future", "politics", "destiny"]},
]

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL UNIQUE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def get_movie(movie_id):
    return next((m for m in MOVIES if m["id"] == movie_id), None)

def recommend_movies(movie, limit=6):
    """Content-based recommendations using genre overlap and shared descriptive tags."""
    scored = []
    for candidate in MOVIES:
        if candidate["id"] == movie["id"]:
            continue
        shared_genres = set(movie["genres"]) & set(candidate["genres"])
        shared_tags = set(movie["tags"]) & set(candidate["tags"])
        # Genre overlap carries more weight; rating gives a small tie-break boost.
        score = len(shared_genres) * 3 + len(shared_tags) + candidate["rating"] / 10
        if score > 0:
            scored.append((score, candidate))
    scored.sort(key=lambda item: (-item[0], -item[1]["rating"], item[1]["title"]))
    return [item[1] for item in scored[:limit]]

def watchlist_ids():
    with connect_db() as conn:
        return {row["movie_id"] for row in conn.execute("SELECT movie_id FROM watchlist")}

@app.route("/")
def index():
    query = request.args.get("q", "").strip().lower()
    genre = request.args.get("genre", "").strip()
    sort = request.args.get("sort", "rating")
    movies = MOVIES
    if query:
        movies = [m for m in movies if query in m["title"].lower() or query in m["description"].lower()]
    if genre:
        movies = [m for m in movies if genre in m["genres"]]
    if sort == "year":
        movies = sorted(movies, key=lambda m: m["year"], reverse=True)
    elif sort == "title":
        movies = sorted(movies, key=lambda m: m["title"].lower())
    else:
        movies = sorted(movies, key=lambda m: m["rating"], reverse=True)
    genres = sorted({g for movie in MOVIES for g in movie["genres"]})
    return render_template("index.html", movies=movies, genres=genres, selected_genre=genre,
                           query=request.args.get("q", ""), sort=sort, watchlist=watchlist_ids())

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = get_movie(movie_id)
    if not movie:
        return render_template("404.html"), 404
    return render_template("detail.html", movie=movie, recommendations=recommend_movies(movie),
                           watchlist=watchlist_ids())

@app.post("/watchlist/add/<int:movie_id>")
def add_watchlist(movie_id):
    if not get_movie(movie_id):
        return jsonify({"error": "Movie not found"}), 404
    try:
        with connect_db() as conn:
            conn.execute("INSERT OR IGNORE INTO watchlist (movie_id) VALUES (?)", (movie_id,))
        flash("Movie added to your watchlist.", "success")
    except sqlite3.Error:
        flash("Could not update the watchlist. Please try again.", "error")
    return redirect(request.referrer or url_for("index"))

@app.post("/watchlist/remove/<int:movie_id>")
def remove_watchlist(movie_id):
    with connect_db() as conn:
        conn.execute("DELETE FROM watchlist WHERE movie_id = ?", (movie_id,))
    flash("Movie removed from your watchlist.", "success")
    return redirect(request.referrer or url_for("watchlist_page"))

@app.route("/watchlist")
def watchlist_page():
    ids = watchlist_ids()
    movies = [m for m in MOVIES if m["id"] in ids]
    movies.sort(key=lambda m: m["title"].lower())
    return render_template("watchlist.html", movies=movies, watchlist=ids)

@app.get("/api/movies")
def api_movies():
    return jsonify({"count": len(MOVIES), "movies": MOVIES})

@app.get("/api/recommend/<int:movie_id>")
def api_recommend(movie_id):
    movie = get_movie(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    return jsonify({"movie": movie["title"], "recommendations": recommend_movies(movie)})

@app.get("/health")
def health():
    return jsonify({"status": "healthy"})

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
