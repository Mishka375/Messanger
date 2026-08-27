FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY libs/ ./libs/
COPY monitoring.py .
COPY database.py .
COPY system.py .
COPY monitor.py .
COPY logs/ ./logs/

CMD ["python", "system.py"]
