FROM python:3.11-slim

WORKDIR /app
COPY app.py /app/app.py

ENV LAB_DB=/data/lab.sqlite3
EXPOSE 8789
VOLUME ["/data"]

CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "8789"]
