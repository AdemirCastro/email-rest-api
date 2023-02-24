FROM alpine

WORKDIR /project

COPY requirements.txt .

COPY ./app ./app

RUN apk add --no-cache python3 py3-pip

RUN pip install -r requirements.txt

CMD ["python", "./app/main.py"]