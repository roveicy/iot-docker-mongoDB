#FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
#RUN rm -rf /app
#
#WORKDIR /app
#
#COPY ./requirements.txt ./requirements.txt
#
#RUN pip install -r ./requirements.txt
#
#COPY . /app
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

EXPOSE 5000

CMD ["gunicorn", "--conf", "/code/app/gunicorn_conf.py", "--bind", "0.0.0.0:5000", "app.main:app"]