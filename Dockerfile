# Use Python 3.9 slim base image (because we're efficient like that)
FROM python:3.9-slim

# Set working directory (your app's home field)
WORKDIR /app

# Copy requirements first (trust me, this matters for build time)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of our app
COPY . .

# Expose port 8000 (let the world in!)
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.BoxOffice:app", "--host", "0.0.0.0", "--port", "8000"]
