FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
RUN rm -rf /app

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ADD ./ /app