FROM python:3.10.13-slim

WORKDIR /app
COPY ./requirements.txt /app
COPY ./telephony_server/twilio_api_server.py /app
COPY ./config.py /app/
COPY vo_utils /app/vo_utils

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pymongo==4.7.2
RUN pip install pydantic-settings==2.3.0
EXPOSE 8001

CMD ["uvicorn", "twilio_api_server:app", "--host", "0.0.0.0", "--port", "8001"]
