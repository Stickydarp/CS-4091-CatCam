# Use a lightweight official Python image
FROM python:3.11-slim


#creating directories for captured data
RUN mkdir -p /catCamData/images /catCamData/metadata


# Set working directory inside container
WORKDIR /app


# Copy dependency file(s)
COPY requirements.txt /requirements.txt


# Install dependencies
RUN pip install --no-cache-dir -r /requirements.txt


# Copy the rest of the application code
COPY . /app

RUN python /app/scripts/setup_environment.py --prepare-host

# Expose whatever port your app uses
EXPOSE 8000


# Run the FastAPI app with uvicorn by default. Use docker exec to run CLI commands if needed.
CMD ["uvicorn", "catCamBackend.server:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]

