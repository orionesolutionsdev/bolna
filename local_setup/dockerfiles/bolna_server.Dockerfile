FROM python:3.10.13-slim

WORKDIR /app
COPY ./requirements.txt /app
COPY ./quickstart_server.py /app
COPY ./endpoints /app/endpoints
COPY ./config.py /app/
COPY vo_utils /app/vo_utils

RUN apt-get update && apt-get install libgomp1 git -y
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg
RUN pip install -r requirements.txt
RUN pip install --force-reinstall git+https://github.com/orionesolutionsdev/bolna@development
RUN pip install scipy==1.11.0
RUN pip install torch==2.0.1
RUN pip install torchaudio==2.0.1
RUN pip install pydub==0.25.1
RUN pip install ffprobe
RUN pip install aiofiles
RUN pip install 'sentry-sdk[fastapi]'
RUN pip install python-multipart
RUN pip install motor==3.4.0
RUN pip install daily-python==0.9.1
EXPOSE 5001
CMD ["uvicorn", "quickstart_server:app", "--host", "0.0.0.0", "--port", "5001"]
