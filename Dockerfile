FROM python:3.12.2-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y apt-utils && apt-get install -y curl
RUN apt-get install git -y
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN pip3 install -r requirements.txt


COPY . .

EXPOSE 5050

CMD ["flask","--app","app", "run", "--host=0.0.0.0", "--port=5050"]