FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/Hamidrz91/phoenix-devops-platform"

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["python", "app.py"]
