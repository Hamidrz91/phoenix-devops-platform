from flask import Flask
import socket
import psycopg2
import os

app = Flask(__name__)

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
