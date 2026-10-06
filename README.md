# CineMap - Film Location Recon API

A FastAPI microservice that matches movie genres, aesthetic vibes, and film titles to real-world travel destinations and travel itineraries.

## Features

- 🎬 **Movie Travel Search (`POST /search`):** Search locations by movie vibe/genre.
- 🎨 **Visual Web Gallery (`/`):** Movie poster style travel destination cards.
- 📖 **Swagger / OpenAPI:** Interactive API documentation served at `/docs`.
- 🧪 **Unit Testing:** `pytest` test suite included.

## How to Run

1. **Setup & Run:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pytest
   uvicorn main:app --reload
   ```
