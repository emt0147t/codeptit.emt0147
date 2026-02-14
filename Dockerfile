FROM python:3.11-slim

# Install gcc/g++ for C/C++ judge
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 10000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
