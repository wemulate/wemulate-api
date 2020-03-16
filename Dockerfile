FROM python:3.7.7

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN apt update

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "interfaces/wsgi:app" ]
