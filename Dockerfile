# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire repo into the container
COPY . .

# Expose port for Flask web server
EXPOSE 3000

# Set environment variables (Railway will override these)
# Example only, do not hardcode sensitive info
# ENV TWITCH_USERNAME=<your_username>
# ENV TWITCH_OAUTH_TOKEN=<your_oauth_token>
# ENV TWITCH_REFRESH_TOKEN=<your_refresh_token>
# ENV CHANNELS=hinya,beansimps
# ENV DISCORD_WEBHOOK_URL=<discord_webhook_url>
# ENV TELEGRAM_TOKEN=<telegram_token>
# ENV TELEGRAM_CHAT_ID=<telegram_chat_id>
# ENV WEBHOOK_URL=<webhook_url>

# Run main.py when container starts
ENTRYPOINT ["python", "main.py"]
