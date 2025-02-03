from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="IMDB Episodes API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Episode(BaseModel):
    id: str
    url: str
    primaryTitle: str
    originalTitle: str
    type: str
    description: Optional[str] = None
    contentRating: Optional[str] = None
    startYear: int
    endYear: Optional[int] = None
    releaseDate: str
    interests: List[str]
    countriesOfOrigin: List[str]
    externalLinks: Optional[str] = None
    spokenLanguages: List[str]
    filmingLocations: List[str]
    productionCompanies: List[dict]  # Assuming it contains name and id
    budget: Optional[int] = None
    grossWorldwide: Optional[int] = None
    genres: List[str]
    isAdult: bool
    runtimeMinutes: int
    averageRating: float
    numVotes: int
    weekendGrossAmount: Optional[int] = None
    weekendGrossCurrency: Optional[str] = None
    lifetimeGrossAmount: Optional[int] = None
    lifetimeGrossCurrency: Optional[str] = None
    weeksRunning: int


class IMDBClient:
    def __init__(self):
        self.api_key = os.getenv('RAPID_API_KEY')
        if not self.api_key:
            raise ValueError("RAPID_API_KEY not found in environment variables")

        self.base_url = "https://imdb236.p.rapidapi.com/imdb/top-box-office"
        self.headers = {
            "x-rapidapi-host": "imdb236.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }

    async def fetch_episodes(self, show_id: str) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/{show_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

    def sort_episodes(self, episodes: List[Dict], sort_by: str = 'averageRating', reverse: bool = True) -> List[Dict]:
        valid_episodes = [ep for ep in episodes if ep.get(sort_by) is not None]
        return sorted(valid_episodes, key=lambda x: x[sort_by], reverse=reverse)

# Initialize IMDB client
imdb_client = IMDBClient()

@app.get("/")
async def root():
    return {"message": "Welcome to the IMDB Episodes API"}

@app.get("/episodes/{show_id}")
async def get_episodes(
    show_id: str,
    sort_by: str = 'averageRating',
    reverse: bool = True
):
    """
    Get episodes for a show with optional sorting

    Parameters:
    - show_id: IMDB ID of the show (e.g., tt7631058)
    - sort_by: Field to sort by (averageRating, numVotes, episodeNumber)
    - reverse: True for descending order, False for ascending
    """
    episodes = await imdb_client.fetch_episodes(show_id)
    sorted_episodes = imdb_client.sort_episodes(episodes, sort_by, reverse)
    return {"episodes": sorted_episodes}

@app.get("/episodes/{show_id}/season/{season_number}")
async def get_season_episodes(
    show_id: str,
    season_number: int,
    sort_by: str = 'episodeNumber',
    reverse: bool = False
):
    """Get episodes for a specific season"""
    episodes = await imdb_client.fetch_episodes(show_id)
    season_episodes = [ep for ep in episodes if ep['seasonNumber'] == season_number]
    sorted_episodes = imdb_client.sort_episodes(season_episodes, sort_by, reverse)
    return {"episodes": sorted_episodes}

@app.get("/episodes/{show_id}/stats")
async def get_show_stats(show_id: str):
    """Get statistics for the show"""
    episodes = await imdb_client.fetch_episodes(show_id)

    # Calculate statistics
    rated_episodes = [ep for ep in episodes if ep['averageRating'] is not None]
    if not rated_episodes:
        return {"error": "No rated episodes found"}

    avg_rating = sum(ep['averageRating'] for ep in rated_episodes) / len(rated_episodes)
    total_votes = sum(ep['numVotes'] for ep in rated_episodes if ep['numVotes'] is not None)

    return {
        "total_episodes": len(episodes),
        "average_rating": round(avg_rating, 2),
        "total_votes": total_votes,
        "seasons": len(set(ep['seasonNumber'] for ep in episodes))
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
