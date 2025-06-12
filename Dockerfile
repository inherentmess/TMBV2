FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Uncomment if using cookies login persistence
# VOLUME ["/usr/src/app/cookies"]

# Uncomment if using the analytics server
# EXPOSE 5000

CMD ["python", "main.py"]
