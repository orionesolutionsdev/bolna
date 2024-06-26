FROM python:3.10.13-slim

WORKDIR /app
COPY ./requirements.txt /app
COPY ./telephony_server/plivo_api_server.py /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002

CMD ["uvicorn", "plivo_api_server:app", "--host", "0.0.0.0", "--port", "8002"]
