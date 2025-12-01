FROM python:3.11-slim

# Install ffmpeg for video processing
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY bot.py .
COPY config.py .
COPY database.py .
COPY ai_processor.py .
COPY video_processor.py .
COPY utils.py .

# Create directory for temporary files
RUN mkdir -p /app/temp

# Run the bot
CMD ["python", "bot.py"]
