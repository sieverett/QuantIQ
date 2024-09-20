# Use an official Python runtime as a parent image
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install WeasyPrint dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libpango1.0-0 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libcairo2 \
    gir1.2-pango-1.0 \
    gir1.2-harfbuzz-0.0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Create a .streamlit directory and copy configuration
RUN mkdir -p ~/.streamlit && cp .streamlit/config.toml ~/.streamlit/config.toml

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Streamlit default port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
