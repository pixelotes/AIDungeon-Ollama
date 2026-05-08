FROM python:3.11.13-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://host.docker.internal:11434
ENV OLLAMA_MODEL=llama2:7b
ENV OLLAMA_TIMEOUT=120
ENV ACTION_SUGGESTIONS=3

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY aidungeon/ ./aidungeon/
COPY interface/ ./interface/
COPY prompts/ ./prompts/
COPY saves/ ./saves/
COPY config.ini web_terminal.py index.html ./

RUN chmod -R 755 /app

# HTTP UI + WebSocket on same port (WS path: /ws)
EXPOSE 8080

CMD ["python", "web_terminal.py"]
