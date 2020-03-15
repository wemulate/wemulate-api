FROM python:3.7.7

RUN apt-get update && apt-get upgrade -y

RUN apt-get install pylint -y

RUN pip3 install virtualenv

CMD [ "bash" ]