FROM python:alpine@sha256:4e8e9a59bf1b3ca8e030244bc5f801f23e41e37971907371da21191312087a07

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wk2mqtt.py .

ENV PYTHONUNBUFFERED=1
CMD [ "python", "./wk2mqtt.py" ]