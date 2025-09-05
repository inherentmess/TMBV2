# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Set environment variables defaults (optional, can override on Railway)
ENV FLASK_ENV=production
ENV PORT=3000

# Expose the port for Railway web server
EXPOSE 3000

# Run the miner
CMD ["python", "main.py"]
