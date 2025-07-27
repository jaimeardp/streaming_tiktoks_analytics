# Use the official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY sa-account.json /app/key.json

ENV GOOGLE_APPLICATION_CREDENTIALS /app/key.json

# Copy source code
COPY . .

# Use gunicorn to serve the app
CMD ["gunicorn", "-b", ":8080", "main:app"]
