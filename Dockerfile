FROM python:alpine@sha256:25df32b602118dab046b58f0fe920e3301da0727b5b07430c8bcd4b139627fdc

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wk2mqtt.py .

ENV PYTHONUNBUFFERED=1
CMD [ "python", "./wk2mqtt.py" ]