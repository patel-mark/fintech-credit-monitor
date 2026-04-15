# Use an official lightweight Python image
FROM python:3.12-slim

WORKDIR /app

# Copy the requirements file first
COPY requirements.txt .

# 1. Test the internet connection so we know exactly what is failing
RUN apt-get update && apt-get install -y curl
RUN curl -I https://pypi.org || echo "NETWORK TEST FAILED"

# 2. Force pip to use IPv4, increase timeout, and trust the host
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_RETRIES=10
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--chdir", "dashboard/dash_app", "app:server"]