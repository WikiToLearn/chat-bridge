FROM python:3.5
RUN pip install flask==0.11.1
RUN pip install pyyaml==3.12
RUN pip install python-telegram-bot==5.0.0
RUN pip install requests==2.11.1
RUN pip install pyee==1.0.2
RUN pip install irc==15.0.1

ADD ./src/ /opt/
WORKDIR /opt/

ADD ./config /etc/chat-bridge/

CMD /opt/app.py

EXPOSE 5000
