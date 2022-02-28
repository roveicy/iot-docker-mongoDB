FROM python:3.9

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ADD ./IoT /app

RUN chmod a+r /app/* && chmod a+rwx /app/run && chmod a+r /app/run/*



CMD [ "/bin/bash", "-c", "/app/run.sh" ]
