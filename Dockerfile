# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the web server port for Railway
EXPOSE 3000

# Run the main script
CMD ["python", "main.py"]
