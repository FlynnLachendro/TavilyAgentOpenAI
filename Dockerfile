# Use a minimal Python 3.13 image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list and install Python dependencies
COPY requirements.txt ./
RUN uv pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8080 for the application
EXPOSE 8080

# Start the application using uvicorn
CMD ["uvicorn", "a2a_main:app", "--host", "0.0.0.0", "--port", "8080"]