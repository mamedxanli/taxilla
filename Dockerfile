FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat
COPY . /src/
RUN pip install -r /src/requirements.txt
EXPOSE 8099
