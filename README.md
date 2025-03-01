# movie_stats-day6-

## Introduction:

This project is a simple API that provides information about movies. It includes the following features:

- **Rating**: Returns a list of movies sorted by rating.
- **Genre**: Returns a list of movies filtered by genre.
- **Highest Opening**: Returns a list of movies with the highest weekend opening gross.

### Available Genres:

Based on the movie descriptions in the API response, here are the possible genres available in this API:

1. **Drama**:

   - The Brutalist
   - A Complete Unknown
   - One of Them Days

2. **Historical / Biographical**:

   - The Brutalist
   - A Complete Unknown

3. **Thriller / Mystery**:

   - Companion

4. **Comedy**:

   - One of Them Days

5. **Action / Adventure**:

   - Sonic the Hedgehog 3

6. **Animation / Family**:
   - Sonic the Hedgehog 3 (if it follows the previous Sonic movies)

## System Design:

![System Design Diagram](/images/box_office.png)

### API Endpoints:

- **GET /movies/rating**: Returns a list of movies sorted by rating.
- **GET /movies/genre**: Returns a list of movies filtered by genre.
- **GET /movies/highest_opening**: Returns a list of movies with the highest weekend opening gross.

### Logging:

Each function logs the following:

- Entry into the function with parameters.
- Successful data retrieval and formatting.
- Errors encountered during execution.

### Environment Variables:

- **API_SECRET_KEY**: The secret key for accessing the API, stored in the `.env` file.

### Running the Application:

To run the application, use the following command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Dockerise Application:

```
docker build . -t boxoffice-app .
docker run -p 8000:8000 --env-file .env --name BoxOfficeApp boxoffice-app
```

### Login to ECR Repository:

```
aws ecr get-login-password | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
```

### Push Docker Image to ECR:

```
docker tag boxoffice-app:latest <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/boxoffice-app:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/boxoffice-app:latest
```

### Rebuild image for M Series mac users:

```
docker buildx build --platform linux/amd64 -t boxoffice-app .
docker tag boxoffice-app:latest 449095351082.dkr.ecr.us-east-1.amazonaws.com/box-office-repo:boxoffice1
docker push 449095351082.dkr.ecr.us-east-1.amazonaws.com/box-office-repo:boxoffice1
```

Test EC2 instance:

```
to test if the application is running
curl http://localhost:8000
```

```
Check movies by rating
curl http://localhost:8000/movies/rating
```

```
Check movies by genre/Comedy
curl http://localhost:8000/movies/genre/comedy
```

```
Check movies by Highest Opening Gross
curl http://localhost:8000/movies/highest_opening
```
