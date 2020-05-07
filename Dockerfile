FROM python:3.7.7

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN apt update

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

WORKDIR /usr/src/app/project

CMD [ "gunicorn", "-b", "0.0.0.0:5000", "wsgi:app", "--timeout", "60" ]
