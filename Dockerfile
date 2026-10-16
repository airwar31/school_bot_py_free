FROM python:3.9-alpine

ENV TZ=Asia/Yekaterinburg
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk update && \
    apk add --no-cache \
    gcc \
    musl-dev \
    sqlite \
    sqlite-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app/

VOLUME ["/app/data"]

CMD ["python", "main.py"]