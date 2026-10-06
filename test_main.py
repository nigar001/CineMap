from unittest.mock import AsyncMock, patch
import httpx
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_visual_ui_route():
    """Verify the live dashboard HTML route responds correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "CineMap Live Movie Recon API" in response.text


@patch("main.httpx.AsyncClient.get")
def test_scout_movie_locations_success(mock_get):
    """Test successful movie lookup with mocked TMDB response."""
    mock_get.return_value = AsyncMock(
        status_code=200,
        json=lambda: {
            "results": [
                {
                    "id": 27205,
                    "title": "Inception",
                    "release_date": "2010-07-15",
                    "overview": "Cobb, a skilled thief...",
                    "vote_average": 8.4,
                    "poster_path": "/8bfL8B0z59R2o1bT7zYg3Q0p1v2.jpg",
                }
            ]
        },
    )

    payload = {"movie_title": "Inception"}
    response = client.post("/api/v2/movie/recon", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Inception"
    assert data["rating"] == 8.4
    assert "https://image.tmdb.org/t/p/w500" in data["poster_url"]


@patch("main.httpx.AsyncClient.get")
def test_scout_movie_not_found(mock_get):
    """Test 404 handling when TMDB returns zero results."""
    mock_get.return_value = AsyncMock(
        status_code=200, json=lambda: {"results": []}
    )

    payload = {"movie_title": "NonExistentMovie123456"}
    response = client.post("/api/v2/movie/recon", json=payload)

    assert response.status_code == 404
    assert (
        "No movies found matching 'NonExistentMovie123456'"
        in response.json()["detail"]
    )


@patch("main.httpx.AsyncClient.get")
def test_tmdb_api_error_handling(mock_get):
    """Test 502 handling when TMDB API returns an error status code."""
    mock_get.return_value = AsyncMock(status_code=401)

    payload = {"movie_title": "Interstellar"}
    response = client.post("/api/v2/movie/recon", json=payload)

    assert response.status_code == 502
    assert "TMDB API returned HTTP 401" in response.json()["detail"]


@patch("main.httpx.AsyncClient.get")
def test_network_connection_error(mock_get):
    """Test 503 handling when a network connection error occurs."""
    mock_get.side_effect = httpx.RequestError("Connection timeout")

    payload = {"movie_title": "Gladiator"}
    response = client.post("/api/v2/movie/recon", json=payload)

    assert response.status_code == 503
    assert "Network error connecting to movie database" in response.json()["detail"]


def test_empty_movie_title_validation():
    """Test 400 validation error for whitespace or empty titles."""
    payload = {"movie_title": "   "}
    response = client.post("/api/v2/movie/recon", json=payload)
    assert response.status_code == 400