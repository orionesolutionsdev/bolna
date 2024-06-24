FROM python:3.10.13-slim

WORKDIR /app
COPY ./requirements.txt /app
COPY ./telephony_server/plivo_api_server.py /app
COPY ./endpoints /app/endpoints
COPY ./config.py /app/
COPY vo_utils /app/vo_utils

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install plivo==4.55.0
RUN pip install 'sentry-sdk[fastapi]'
RUN pip install python-multipart
RUN pip install motor==3.4.0
RUN pip install pydantic-settings==2.2.1
EXPOSE 8002

CMD ["uvicorn", "plivo_api_server:app", "--host", "0.0.0.0", "--port", "8002"]
