import os
import requests
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from enum import Enum
from tabulate import tabulate
from fastapi.responses import PlainTextResponse, HTMLResponse

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

class MovieSummary(BaseModel):
    primaryTitle: str
    averageRating: float
    releaseDate: str
    weekendGrossAmount: Optional[int]
    description: str

class SortOption(str, Enum):
    RATING = "rating"
    GROSS = "gross"
    RELEASE = "release"
    TITLE = "title"

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

@app.get("/movies", response_model=List[MovieSummary])
async def get_movies(
    sort_by: SortOption = Query(
        default=SortOption.GROSS,
        description="Sort by: rating, gross, release, or title"
    ),
    limit: int = Query(
        default=5,
        le=10,
        description="Number of movies to return (max 10)"
    )
):
    logger.info(f"Fetching movies with sort_by={sort_by} and limit={limit}")
    
    movies = imdb_client.get_box_office_movies()
    
    # Sort movies based on selected option
    if sort_by == SortOption.RATING:
        movies.sort(key=lambda x: x.averageRating or 0, reverse=True)
    elif sort_by == SortOption.GROSS:
        movies.sort(key=lambda x: x.weekendGrossAmount or 0, reverse=True)
    elif sort_by == SortOption.RELEASE:
        movies.sort(key=lambda x: x.releaseDate or "", reverse=True)
    else:  # sort by title
        movies.sort(key=lambda x: x.primaryTitle)
    
    # Limit results
    movies = movies[:limit]
    
    logger.info(f"Returning {len(movies)} movies sorted by {sort_by}")
    return movies

@app.get("/movies/table", response_class=PlainTextResponse)
async def get_movies_table(
    sort_by: SortOption = Query(
        default=SortOption.GROSS,
        description="Sort by: rating, gross, release, or title"
    ),
    limit: int = Query(
        default=5,
        le=10,
        description="Number of movies to return (max 10)"
    )
):
    logger.info(f"Fetching movies table with sort_by={sort_by} and limit={limit}")
    
    movies = imdb_client.get_box_office_movies()
    
    # Sort movies based on selected option
    if sort_by == SortOption.RATING:
        movies.sort(key=lambda x: x.averageRating or 0, reverse=True)
    elif sort_by == SortOption.GROSS:
        movies.sort(key=lambda x: x.weekendGrossAmount or 0, reverse=True)
    elif sort_by == SortOption.RELEASE:
        movies.sort(key=lambda x: x.releaseDate or "", reverse=True)
    else:  # sort by title
        movies.sort(key=lambda x: x.primaryTitle)
    
    # Limit results and prepare table data
    movies = movies[:limit]
    table_data = [
        [
            m.primaryTitle,
            f"{m.averageRating:.1f}",
            m.releaseDate,
            f"${m.weekendGrossAmount:,}" if m.weekendGrossAmount else "N/A",
            m.description[:50] + "..." if len(m.description) > 50 else m.description
        ] for m in movies
    ]
    
    headers = ["Title", "Rating", "Release Date", "Weekend Gross", "Description"]
    table = tabulate(table_data, headers=headers, tablefmt="grid")
    
    logger.info(f"Returning formatted table with {len(movies)} movies")
    return table

@app.get("/movies/rating", response_class=HTMLResponse)
async def get_movies_rating(
    sort_by: SortOption = Query(
        default=SortOption.RATING,
        description="Sort by: rating, gross, release, or title"
    ),
    limit: int = Query(
        default=5,
        le=10,
        description="Number of movies to return (max 10)"
    )
):
    try:
        logger.info(f"Fetching movies table with sort_by={sort_by} and limit={limit}")
        
        movies = imdb_client.get_box_office_movies()
        
        # Sort movies based on rating
        movies = [m for m in movies if m.averageRating]
        movies.sort(key=lambda x: x.averageRating, reverse=True)
        movies = movies[:limit]
        
        # Format data for response
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                "title": movie.primaryTitle,
                "rating": f"{movie.averageRating:.1f}",
                "gross": f"${movie.weekendGrossAmount:,.2f}" if movie.weekendGrossAmount else "N/A",
                "release": movie.startYear,
                "runtime": f"{movie.runtimeMinutes} min"
            })

        headers = ["Title", "Rating", "Gross", "Release", "Runtime"]
        table_data = [
            [
                movie["title"],
                movie["rating"],
                movie["gross"],
                movie["release"],
                movie["runtime"]
            ] for movie in formatted_movies
        ]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        logger.info(f"Returning {len(formatted_movies)} movies in table format")
        return HTMLResponse(content=f"<pre>{table}</pre>")
        
    except Exception as e:
        logger.error(f"Error fetching movie ratings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

#Sort latest movies by genre
@app.get("/movies/genre", response_class=HTMLResponse)
async def get_movies_genre(
    genre: str = Query(
        default="Action",
        description="Genre of the movie"
    ),
    limit: int = Query(
        default=5,
        le=10,
        description="Number of movies to return (max 10)"
    )
):
    try:
        logger.info(f"Fetching movies with genre={genre} and limit={limit}")

        movies = imdb_client.get_box_office_movies()

        # Filter movies by genre
        movies = [m for m in movies if genre in m.genres]
        movies = movies[:limit]

        # Format data for response
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                "title": movie.primaryTitle,
                "rating": f"{movie.averageRating:.1f}",
                "gross": f"${movie.weekendGrossAmount:,.2f}" if movie.weekendGrossAmount else "N/A",
                "release": movie.startYear,
                "runtime": f"{movie.runtimeMinutes} min"
            })

        headers = ["Title", "Rating", "Gross", "Release", "Runtime"]
        table_data = [
            [
                movie["title"],
                movie["rating"],
                movie["gross"],
                movie["release"],
                movie["runtime"]
            ] for movie in formatted_movies
        ]
        table = tabulate(table_data, headers=headers, tablefmt="grid")

        logger.info(f"Returning {len(formatted_movies)} movies with genre {genre}")
        return HTMLResponse(content=f"<pre>{table}</pre>")

    except Exception as e:
        logger.error(f"Error fetching movies by genre: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

#highest weekend opening.
@app.get("/movies/highest_opening", response_class=HTMLResponse)
async def get_movies_highest_opening(
    limit: int = Query(
        default=5,
        le=10,
        description="Number of movies to return (max 10)"
    )
):
    try:
        logger.info(f"Fetching movies with highest opening and limit={limit}")

        movies = imdb_client.get_box_office_movies()

        # Sort movies based on weekend gross
        movies = [m for m in movies if m.weekendGrossAmount]
        movies.sort(key=lambda x: x.weekendGrossAmount, reverse=True)
        movies = movies[:limit]

        # Format data for response
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                "title": movie.primaryTitle,
                "rating": f"{movie.averageRating:.1f}",
                "gross": f"${movie.weekendGrossAmount:,.2f}" if movie.weekendGrossAmount else "N/A",
                "release": movie.startYear,
                "runtime": f"{movie.runtimeMinutes} min"
            })

        headers = ["Title", "Rating", "Gross", "Release", "Runtime"]
        table_data = [
            [
                movie["title"],
                movie["rating"],
                movie["gross"],
                movie["release"],
                movie["runtime"]
            ] for movie in formatted_movies
        ]
        table = tabulate(table_data, headers=headers, tablefmt="grid")

        logger.info(f"Returning {len(formatted_movies)} movies with highest opening")
        return HTMLResponse(content=f"<pre>{table}</pre>")

    except Exception as e:
        logger.error(f"Error fetching movies with highest opening: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
