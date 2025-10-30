FROM python:3.11-alpine3.18

RUN apk add --no-cache git

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD [ "python", "start.py" ]
