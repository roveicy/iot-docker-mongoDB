FROM python:3.9-alpine

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY . /app

RUN mkdir "/app/run/"

RUN chmod a+rwx "/app/run/"

CMD [ "python",  "/app/main.py"]
