FROM python:alpine@sha256:995c7fcdf9a10e0e1a4555861dac63436b456822a167f07b6599d4f105de6fa0

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wk2mqtt.py .

ENV PYTHONUNBUFFERED=1
CMD [ "python", "./wk2mqtt.py" ]