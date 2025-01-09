FROM python:3.11.11-alpine

ENV TG_BOT_TOKEN ""
ENV CONFIG_FILE ""

ADD requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt;

ADD scripts/ /opt/anti_slip_bot/scripts/
ADD configs/ /opt/anti_slip_bot/configs/

WORKDIR /opt/anti_slip_bot

ENTRYPOINT [ "/usr/local/bin/python3", "/opt/anti_slip_bot/scripts/anti_slip_bot.py" ]
