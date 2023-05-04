FROM python:alpine@sha256:721023564970262d6ac79d30e2a2399d32555220e4f37bfe2c3a687b4f9721d9

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wk2mqtt.py .

ENV PYTHONUNBUFFERED=1
CMD [ "python", "./wk2mqtt.py" ]