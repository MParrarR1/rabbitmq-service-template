FROM ubuntu:latest

RUN apt-get clean
RUN apt-get update -y

RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install python3.12-venv -y

ADD *.py /
ADD database ./database
ADD config.json /
ADD requirements.txt /


RUN python3 -m venv venv
RUN . venv/bin/activate
RUN venv/bin/pip3 install --upgrade pip
RUN venv/bin/pip3 install -r requirements.txt

EXPOSE 80

CMD [ "venv/bin/python3", "-u", "main.py" ]
