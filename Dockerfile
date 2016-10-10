FROM wikitolearn/python35:0.1

RUN pip install flask==0.11.1
RUN pip install python-telegram-bot==5.0.0
RUN pip install pyee==1.0.2
RUN pip install irc==15.0.1
RUN pip install tqdm==4.8.4

ADD ./src/ /opt/
WORKDIR /opt/

ENV PYTHONUNBUFFERED=0

CMD /opt/app.py

EXPOSE 5000
