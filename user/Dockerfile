FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./system/libs/ ./libs/

EXPOSE 70

RUN mkdir logs && touch logs/main_log

COPY ./system/monitor.py .

CMD ["python", "monitor.py"]