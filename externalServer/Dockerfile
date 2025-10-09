# Use a lightweight official Python image
FROM python:3.11-slim


#creating directories for captured data
RUN mkdir -p /catCamData/images /catCamData/metadata


# Set working directory inside container
WORKDIR /app


# Copy dependency file(s)
COPY requirements.txt /app/requirements.txt


# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt


# Copy the rest of the application code
COPY . /app


# Expose whatever port your app uses
EXPOSE 8000


# The command to run your app. Adjust path/command as needed.
# For example, if your FastAPI app is in src/catcam_backend/main.py:
CMD ["uvicorn", "catcam_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

