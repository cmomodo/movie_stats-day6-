import os
import requests
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IMDB Episodes API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductionCompany(BaseModel):
    id: str
    name: str

class Movie(BaseModel):
    id: str
    url: str
    primaryTitle: str
    originalTitle: str
    type: str
    description: Optional[str]
    primaryImage: Optional[str]
    contentRating: Optional[str]
    startYear: Optional[int]
    endYear: Optional[int]
    releaseDate: Optional[str]
    interests: Optional[List[str]]
    countriesOfOrigin: Optional[List[str]]
    externalLinks: Optional[List[str]] = None  # Changed to list of strings
    spokenLanguages: Optional[List[str]]
    filmingLocations: Optional[List[str]]
    productionCompanies: Optional[List[ProductionCompany]]
    budget: Optional[int]
    grossWorldwide: Optional[int]
    genres: Optional[List[str]]
    isAdult: bool
    runtimeMinutes: Optional[int]
    averageRating: Optional[float]
    numVotes: Optional[int]
    weekendGrossAmount: Optional[int]
    weekendGrossCurrency: Optional[str]
    lifetimeGrossAmount: Optional[int]
    lifetimeGrossCurrency: Optional[str]
    weeksRunning: Optional[int]

class IMDBClient:
    def __init__(self):
        logger.info("Initializing IMDBClient.")
        self.api_key = os.getenv('RAPID_API_KEY')
        if not self.api_key:
            logger.error("RAPID_API_KEY not found in environment variables.")
            raise ValueError("RAPID_API_KEY not found in environment variables")
        self.base_url = "https://imdb236.p.rapidapi.com/imdb/top-box-office"
        self.headers = {
            "x-rapidapi-host": "imdb236.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }

    def get_box_office_movies(self) -> List[Movie]:
        logger.info("Fetching box office movies from IMDB.")
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch movies. Status: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
        logger.info("Movies fetched successfully.")
        return [Movie(**item) for item in response.json()]

# Initialize IMDB client
imdb_client = IMDBClient()

@app.get("/")
async def root():
    logger.info("Root endpoint called.")
    return {"message": "Welcome to the IMDB Episodes API"}

@app.get("/movies", response_model=List[Movie])
async def get_movies():
    logger.info("Retrieving movies from IMDB client.")
    movies = imdb_client.get_box_office_movies()
    logger.info("Returning movies data.")
    return movies

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
