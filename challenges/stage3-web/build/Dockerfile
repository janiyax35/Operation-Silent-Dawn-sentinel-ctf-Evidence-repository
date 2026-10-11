FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY init_db.py .
COPY templates ./templates

RUN python init_db.py

EXPOSE 8080

USER 65532:65532

CMD ["python", "app.py"]