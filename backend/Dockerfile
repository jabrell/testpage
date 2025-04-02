FROM python:3.12.8-bullseye

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create a service user ("svcuser") and permit it on /app. Switch to the user. See https://docs.docker.com/reference/dockerfile/#run and https://docs.docker.com/reference/dockerfile/#user.
RUN useradd -r -u 1001 svcuser && \
    chown -R svcuser:svcuser /app
USER svcuser:svcuser

EXPOSE 8000/tcp

# Start the Python-based ASGI web server, uvicorn, listening on all network interfaces on port 8000/tcp. See https://docs.docker.com/reference/dockerfile/#cmd.
# CMD ["python", "-m", "uvicorn", "--app-dir", "./app", "main:app", "--host=0.0.0.0", "--port=8000"]
CMD ["fastapi", "run", "--workers", "4", "app/main.py"]

