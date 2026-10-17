FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# For pure Python app, requirements can be minimal or empty
COPY app.py .

EXPOSE 8000

CMD ["python3", "app.py"]
