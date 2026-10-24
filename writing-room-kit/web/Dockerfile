# Build from the repository root:  fly deploy --config writing-room-kit/web/fly.toml --dockerfile writing-room-kit/web/Dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn httpx python-dotenv pydantic
COPY shared/llm.py shared/llm.py
COPY writing-room-kit/data/corpus.json writing-room-kit/data/answer-key.json writing-room-kit/data/
COPY writing-room-kit/v04/policies writing-room-kit/v04/policies
COPY writing-room-kit/v04/llmx.py writing-room-kit/v04/room.py writing-room-kit/v04/finalize.py writing-room-kit/v04/lineage.py writing-room-kit/v04/lineage2.py writing-room-kit/v04/
COPY writing-room-kit/web/app.py writing-room-kit/web/examples.json writing-room-kit/web/
COPY writing-room-kit/web/static writing-room-kit/web/static
ENV ROOM_SESSIONS_DIR=/tmp/room-sessions PORT=8080
WORKDIR /app/writing-room-kit/web
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
