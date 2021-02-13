FROM alpine:latest

RUN apk update && apk add --no-cache python3 py-pip && python3 -m pip install --upgrade pip

WORKDIR /app

COPY requirements.txt main.py /app/

RUN python3 -m pip install --no-cache-dir -r requirements.txt

CMD python3 main.py $PORT