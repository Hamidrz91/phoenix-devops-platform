from flask import Flask, Response, request, g
import socket
import psycopg2
import os
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "phoenix_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "phoenix_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

@app.before_request
def start_request_timer():
    g.request_start_time = time.perf_counter()

@app.after_request
def record_request(response):
    endpoint = request.endpoint or "unknown"

    if endpoint == "metrics":
        return response

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(time.perf_counter() - g.request_start_time)

    return response


@app.route("/")
def home():
    return f"""
    <h1>🔥 Phoenix DevOps Platform</h1>
    <p>Application is running inside a Docker container.</p>
    <p>Hostname: {socket.gethostname()}</p>
    """

@app.route("/health")
def health():
    return {"status": "healthy"}

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)

@app.route("/db-check")
def db_check():
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "db"),
            dbname=os.environ.get("DB_NAME", "phoenix_db"),
            user=os.environ.get("DB_USER", "phoenix"),
            password=os.environ["DB_PASSWORD"],
            connect_timeout=3
        )
        conn.close()
        return {"database": "connected"}
    except Exception as e:
        return {"database": "failed", "error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
