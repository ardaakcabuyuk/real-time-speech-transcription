# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for PyAudio and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    espeak \
    vorbis-tools \
    sox \
    alsa-utils \
    libasound2 \
    libasound2-plugins \
    libportaudio2 \
    libportaudiocpp0 \
    pulseaudio \
    pulseaudio-utils \
    portaudio19-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the application command
CMD ["python", "main.py"]
