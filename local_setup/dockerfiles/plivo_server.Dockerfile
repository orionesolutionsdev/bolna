FROM python:3.10.13-slim
WORKDIR /app
COPY telephony_server/requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt
COPY telephony_server/plivo_api_server.py config.py /app/
COPY vo_utils /app/vo_utils
EXPOSE 8002
CMD ["uvicorn", "plivo_api_server:app", "--host", "0.0.0.0", "--port", "8002"]
