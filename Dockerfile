# Use the official lightweight Python image
FROM python:3.12-slim

# Set environment variables to prevent Python from generating .pyc files and to buffer output for easier debugging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    firefox-esr \
    xvfb \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libxrender1 \
    libxcomposite1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install geckodriver (required for Selenium with Firefox)
RUN wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.36.0-linux64.tar.gz \
    && tar -xvzf geckodriver-v0.36.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && rm geckodriver-v0.36.0-linux64.tar.gz

# Copy the requirements.txt file (if you have one) and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the scraper script into the container
COPY src/elibDownload.py /app/src/elibDownload.py

# Set the default command to run the scraper script
CMD ["python", "src/elibDownload.py"]
