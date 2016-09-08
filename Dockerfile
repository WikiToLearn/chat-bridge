FROM python:3.5
RUN pip install flask
RUN pip install pyyaml
RUN pip install python-telegram-bot
RUN pip install requests
RUN pip install python-ddp

ADD ./src/ /opt/
WORKDIR /opt/

ADD ./config /etc/chat-bridge/

CMD /opt/app.py

EXPOSE 5000
