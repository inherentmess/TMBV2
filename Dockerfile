# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Set environment variable for Flask
ENV FLASK_APP=main.py

# Expose port for Railway
EXPOSE 3000

# Run the app
CMD ["python", "main.py"]
