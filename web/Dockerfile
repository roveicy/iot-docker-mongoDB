FROM tiangolo/uwsgi-nginx-flask:python3.7
RUN rm -rf /app

RUN mkdir "/app"

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ADD ./ /app