# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Railway web server
EXPOSE 3000

# Set environment variables for Railway (optional defaults)
ENV PORT=3000

# Run main.py
ENTRYPOINT ["python", "main.py"]
