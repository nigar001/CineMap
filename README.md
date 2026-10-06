# CineMap - Film Location Recon API

A FastAPI microservice that matches movie genres, aesthetic vibes, and film titles to real-world travel destinations and travel itineraries.

## Features

- 🎬 **Movie Travel Search (`POST /search`):** Search locations by movie vibe/genre.
- 🎨 **Visual Web Gallery (`/`):** Movie poster style travel destination cards.
- 📖 **Swagger / OpenAPI:** Interactive API documentation served at `/docs`.
- 🧪 **Unit Testing:** `pytest` test suite included.

## 🎯 Project Purpose & Concept

### The Problem

When moviegoers watch visually captivating films—whether it's the futuristic cityscape of _Blade Runner 2049_, the desert dunes of _Dune_, or the alpine landscapes of _Inception_—they often wonder, _"Where was that filmed, and how can I visit places with that exact visual aesthetic?"_ Manually digging through film databases and travel blogs is fragmented and time-consuming.

### The Solution

**CineMap** bridges film metadata and travel scouting into a single, unified API microservice.

By querying real-time data from **The Movie Database (TMDB)**, CineMap matches live movie telemetry—including official artwork, community ratings, and plot synopses—with real-world shoot locations and seasonal travel windows.

### Key Engineering Goals

- **Live Data Integration:** Replaces static/mocked data with non-blocking asynchronous REST requests (`httpx`).
- **Production Security:** Enforces strict secret isolation by injecting API credentials through environment variables (`.env`).
- **Developer-Centric OpenAPI Schema:** Generates interactive, self-documenting Swagger UI endpoints using **Pydantic V2** data models, Enums, and explicit HTTP error handling (`400`, `404`, `502`, `503`).
- **Offline Reliability:** Provides a robust `pytest` suite that uses network mocks (`AsyncMock`) to test API logic without consuming live API quotas or requiring an active internet connection.

## How to Run

1. **Setup & Run:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pytest
   uvicorn main:app --reload
   ```
