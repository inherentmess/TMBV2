# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements first (cache optimization)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the web server port
EXPOSE 3000

# Run the miner
CMD ["python", "main.py"]
