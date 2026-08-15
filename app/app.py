from flask import Flask
import socket

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
