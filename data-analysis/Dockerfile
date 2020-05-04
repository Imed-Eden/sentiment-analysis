FROM python:3.8.0-slim
LABEL maintainer="Imed Eden"

RUN pip install --upgrade pip
RUN pip install azure-ai-textanalytics

WORKDIR /home/root
COPY . .

USER root

ENTRYPOINT ["python", "sentiment.py"]
