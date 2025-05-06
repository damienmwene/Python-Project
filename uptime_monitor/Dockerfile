# Use the official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy the Python script and requirements
COPY uptime_monitor.py .
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script
CMD ["python", "uptime_monitor.py"]
