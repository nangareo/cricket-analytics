# ============================================
# DOCKERFILE - Cricket Analytics
# ============================================

# Start from official Python image
# Think of this as a clean laptop with Python installed
FROM python:3.11-slim

# Set working directory inside container
# Like doing: cd /app
WORKDIR /app

# Copy requirements first (for faster rebuilds)
COPY requirements.txt .

# Install all Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Create output directories
RUN mkdir -p analytics/batting \
             analytics/bowling \
             analytics/fielding \
             analytics/allrounder \
             data

# Default command when container runs
CMD ["python", "analytics/batting/batting_scorer.py"]