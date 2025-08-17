FROM python:3.11.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://host.docker.internal:11434

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY aidungeon/ ./aidungeon/
COPY config.ini .
COPY launch.py .
COPY web_terminal.py .
COPY index.html .
COPY interface/ ./interface/
COPY prompts/ ./prompts/
COPY saves/ ./saves/

# Set proper permissions
RUN chmod -R 755 /app

# Expose ports for web interface
EXPOSE 8080 8765

# Run the application
CMD ["python", "web_terminal.py"]