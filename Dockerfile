# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies for wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    xfonts-base \
    xfonts-75dpi 

# Add wkhtmltopdf to the system PATH
ENV PATH="/usr/bin/wkhtmltopdf:$PATH"

# Copy project files
COPY . /app

# This sets the /app directory as the working directory for any RUN, CMD, ENTRYPOINT, or COPY instructions that follow.
WORKDIR /app

# This command creates a .streamlit directory in the home directory of the container.
RUN mkdir ~/.streamlit

# This copies your Streamlit configuration file into the .streamlit directory you just created.
RUN cp .streamlit/config.toml ~/.streamlit/config.toml

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Streamlit default port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "quantiq.py", "--server.port=8501", "--server.address=0.0.0.0"]
