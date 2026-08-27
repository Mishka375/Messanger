FROM python:3.11-slim

WORKDIR /app

COPY ./system/libs/ ./libs/
COPY ./system/monitor.py .

RUN mkdir logs && touch logs/main_log

EXPOSE 70
EXPOSE 71

CMD ["python", "monitor.py"]