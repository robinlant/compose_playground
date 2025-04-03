FROM python:3.12

WORKDIR /app

COPY . .

RUN ["pip", "install", "-r", "requirements.txt"]

WORKDIR /app/test/integration

ENTRYPOINT ["pytest"]