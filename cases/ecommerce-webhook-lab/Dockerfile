FROM python:3.11-slim

WORKDIR /app
COPY app.py /app/app.py

ENV LAB_DB=/data/lab.sqlite3
EXPOSE 8789
VOLUME ["/data"]

# Keep container orchestration aware of application-level readiness without
# adding curl or another runtime dependency to the slim image.
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8789/health', timeout=2)"

CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "8789"]
