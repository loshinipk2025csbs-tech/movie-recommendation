import os
import tempfile
import unittest

# Set a temporary database before importing the application.
_fd, _db_path = tempfile.mkstemp(suffix=".sqlite")
os.close(_fd)
os.environ["MOVIE_DB_PATH"] = _db_path

from app import app, recommend_movies, MOVIES

class MovieRecommendationTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CineMatch", response.data)

    def test_search_filters_movies(self):
        response = self.client.get("/?q=Inception")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Inception", response.data)
        self.assertNotIn(b"Finding Nemo", response.data)

    def test_recommendations_exclude_selected_movie(self):
        movie = next(m for m in MOVIES if m["title"] == "Inception")
        results = recommend_movies(movie)
        self.assertTrue(results)
        self.assertNotIn(movie["id"], [m["id"] for m in results])

    def test_recommendation_api(self):
        response = self.client.get("/api/recommend/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"recommendations", response.data)

    def test_unknown_movie_api_returns_404(self):
        response = self.client.get("/api/recommend/9999")
        self.assertEqual(response.status_code, 404)

    def test_watchlist_add_and_view(self):
        response = self.client.post("/watchlist/add/1", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        watchlist_response = self.client.get("/watchlist")
        self.assertIn(b"Inception", watchlist_response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"healthy", response.data)

if __name__ == "__main__":
    unittest.main()
