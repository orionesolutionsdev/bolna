FROM python:3.10.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    git \
    ffmpeg
COPY ./requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY quickstart_server.py config.py /app/
COPY endpoints /app/endpoints
COPY vo_utils /app/vo_utils
COPY ambient_music_files /app/ambient_music_files
EXPOSE 5001
CMD ["uvicorn", "quickstart_server:app", "--host", "0.0.0.0", "--port", "5001"]
