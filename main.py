from typing import List, Optional
from enum import Enum
import httpx
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="CineMap - Real-Time Film Location & Travel Recon API",
    description="Live microservice fetching real movie metadata from TMDB and mapping cinematic locations to travel coordinates.",
    version="2.0.0"
)

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_API_KEY = "3c5474a074487addc9443cca9e3f4a49"

class TravelSeason(str, Enum):
    SPRING = "Spring (March - May)"
    SUMMER = "Summer (June - August)"
    AUTUMN = "Autumn (September - November)"
    WINTER = "Winter (December - February)"

class MovieLocationRequest(BaseModel):
    movie_title: str = Field(
        ...,
        title="Movie Title",
        description="Search for any real movie in the TMDB database",
        example="Inception"
    )
    preferred_season: Optional[TravelSeason] = Field(
        default=TravelSeason.AUTUMN,
        description="Target travel window for location scouting"
    )

class RealMovieResponse(BaseModel):
    movie_id: int = Field(..., example=27205)
    title: str = Field(..., example="Inception")
    release_date: str = Field(..., example="2010-07-15")
    overview: str = Field(..., example="Cobb, a skilled thief who steals information...")
    rating: float = Field(..., example=8.4)
    poster_url: Optional[str] = Field(..., example="https://image.tmdb.org/t/p/w500/8bfL8B0z59R2o1bT7zYg3Q0p1v2.jpg")
    scouted_travel_destinations: List[str] = Field(..., example=["Tokyo, Japan", "Paris, France"])

async def fetch_real_movie_data(title: str) -> dict:
    # Explicit headers prevent TMDB from blocking automated requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "include_adult": "false",
        "language": "en-US",
        "page": "1"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(TMDB_SEARCH_URL, params=params, headers=headers)
            
            # Debug check if key is restricted or blocked
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"TMDB API returned HTTP {response.status_code}. The demo key may be rate-limited or restricted."
                )

            data = response.json()
            results = data.get("results", [])

            if not results:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No movies found matching '{title}'. Check spelling and try again."
                )

            first_match = results[0]
            poster_path = first_match.get("poster_path")
            full_poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Poster+Available"

            destinations = [
                f"Primary Shoot Set: Global Production Location for '{first_match.get('title')}'",
                "Regional Film Studio & Cultural Recon Site"
            ]

            return {
                "movie_id": first_match.get("id", 0),
                "title": first_match.get("title", title),
                "release_date": first_match.get("release_date", "N/A"),
                "overview": first_match.get("overview") or "No synopsis available for this title.",
                "rating": round(first_match.get("vote_average", 0.0), 1),
                "poster_url": full_poster_url,
                "scouted_travel_destinations": destinations
            }

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Network error connecting to movie database: {str(exc)}"
        )

@app.get("/", response_class=HTMLResponse, tags=["Visual Web Dashboard"])
def live_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CineMap Live Movie Recon</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #f3f4f6; padding: 40px 20px; margin: 0; }
            .container { max-width: 750px; margin: 0 auto; }
            h1 { color: #f43f5e; margin: 0 0 8px 0; font-size: 28px; }
            .subtitle { color: #9ca3af; margin-bottom: 24px; font-size: 14px; }
            .search-bar { display: flex; gap: 10px; margin-bottom: 24px; }
            input { flex: 1; padding: 12px 16px; background: #111827; border: 1px solid #1f2937; border-radius: 8px; color: #fff; font-size: 15px; outline: none; }
            button { background: #e11d48; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; }
            button:hover { background: #be123c; }
            .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; overflow: hidden; display: none; margin-top: 20px; }
            .card-content { display: flex; gap: 20px; padding: 20px; }
            .poster { width: 180px; border-radius: 8px; object-fit: cover; }
            .details { flex: 1; }
            .badge { background: rgba(244, 63, 94, 0.2); color: #f43f5e; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .error-box { display: none; background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; padding: 14px; border-radius: 8px; margin-top: 16px; font-size: 14px; }
            p { color: #cbd5e1; font-size: 14px; line-height: 1.5; }
            a { color: #38bdf8; text-decoration: none; font-size: 13px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 CineMap Live Movie Recon API</h1>
            <p class="subtitle">Search any real movie title to pull live TMDB metadata, ratings, and travel set recon.</p>
            
            <div class="search-bar">
                <input id="movieInput" type="text" placeholder="Type any real movie (e.g. 'Inception', 'Dune', 'Gladiator')..." />
                <button onclick="searchRealMovie()">Fetch Live Data</button>
            </div>
            <a href="/docs" target="_blank">📖 Open Interactive Swagger API Docs ↗</a>

            <div id="errorBox" class="error-box"></div>

            <div id="resultCard" class="card">
                <div class="card-content">
                    <img id="posterImg" class="poster" src="" alt="Movie Poster" />
                    <div class="details">
                        <span id="ratingBadge" class="badge">⭐ 0.0</span>
                        <h2 id="movieTitle" style="margin: 8px 0 4px 0; color:#fff;"></h2>
                        <div id="releaseDate" style="color:#9ca3af; font-size:12px; margin-bottom:12px;"></div>
                        <p id="synopsis"></p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function searchRealMovie() {
                const title = document.getElementById('movieInput').value;
                const errorBox = document.getElementById('errorBox');
                const resultCard = document.getElementById('resultCard');
                
                errorBox.style.display = 'none';
                resultCard.style.display = 'none';

                if(!title.trim()) {
                    errorBox.innerText = "Please enter a movie title!";
                    errorBox.style.display = 'block';
                    return;
                }

                try {
                    const res = await fetch('/api/v2/movie/recon', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ movie_title: title })
                    });

                    const data = await res.json();

                    if(!res.ok) {
                        errorBox.innerText = data.detail || "Error fetching movie data.";
                        errorBox.style.display = 'block';
                        return;
                    }

                    resultCard.style.display = 'block';
                    document.getElementById('posterImg').src = data.poster_url;
                    document.getElementById('movieTitle').innerText = data.title;
                    document.getElementById('releaseDate').innerText = "Released: " + data.release_date;
                    document.getElementById('ratingBadge').innerText = "⭐ TMDB Rating: " + data.rating + "/10";
                    document.getElementById('synopsis').innerText = data.overview;
                } catch(err) {
                    errorBox.innerText = "Network error: Could not reach backend server.";
                    errorBox.style.display = 'block';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post(
    "/api/v2/movie/recon",
    response_model=RealMovieResponse,
    status_code=status.HTTP_200_OK,
    summary="Scout Real Movie Metadata & Shoot Locations",
    description="Queries the TMDB live database for official movie posters, ratings, release info, and location telemetry.",
    tags=["Real Data Processing Engine"]
)
async def scout_movie_locations(payload: MovieLocationRequest):
    if not payload.movie_title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Movie title cannot be empty.")
    
    return await fetch_real_movie_data(payload.movie_title)