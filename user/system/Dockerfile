FROM python:3.14

WORKDIR /app

COPY libs/ ./libs/
COPY monitor.py .

RUN mkdir logs && touch logs/main_log

EXPOSE 70
EXPOSE 71

CMD ["python", "monitor.py"]