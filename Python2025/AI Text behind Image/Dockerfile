# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for data
RUN mkdir -p sample_images output

# Download sample images and models
RUN python ai_text_behind_image.py samples
RUN python ai_text_behind_image.py models

# Expose port for Streamlit
EXPOSE 8501

# Command to run the application
CMD ["python", "ai_text_behind_image.py", "run", "--app", "advanced", "--port", "8501"]