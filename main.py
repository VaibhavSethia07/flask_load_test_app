import time
from urllib import request
from flask import Flask
from prometheus_client import make_wsgi_app, Counter, Histogram, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

REQUESTS = Counter("http_requests_total",
                   "Total number of requests", labelnames=["path", "method"])

LATENCY = Histogram("request_latency_seconds",
                    "Request latency", labelnames=["path", "method"])

IN_PROGRESS = Gauge("inprogress_requests",
                    "Total number of requests in progress", labelnames=["path", "method"])

app = Flask(__name__)

# Add prometheus middleware to export metrics at /metrics
app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": make_wsgi_app()})


def before_request():
    IN_PROGRESS.labels(request.method, request.path).inc()
    request.start_time = time.time()


def after_request(response):
    IN_PROGRESS.labels(request.method, request.path).dec()
    request_latency = time.time()-request.start_time
    LATENCY.labels(request.method, request.path).observe(request_latency)
    return response


@app.get("/cars")
def get_cars():
    REQUESTS.labels("/cars", "get").inc()
    return ["toyota", "honda", "mazda", "lexus"]


@app.get("/cars/<int:id>")
def get_car(id):
    REQUESTS.labels("/cars", "get").inc()
    return "Single car"


@app.post("/cars")
def post_car():
    REQUESTS.labels("/cars", "post").inc()
    return "Creating car"


@app.patch("/cars/<int:id>")
def update_car():
    REQUESTS.labels("/cars", "patch").inc()
    return "Updating car"


@app.delete("/cars/<int:id>")
def delete_car():
    REQUESTS.labels("/cars", "delete").inc()
    return "Deleting car"


@app.get("/boats")
def get_boats():
    REQUESTS.labels("/boats", "get").inc()
    return ["boat1", "boat2", "boat3", "boat4"]


@app.post("/boats")
def create_boat():
    REQUESTS.labels("/boats", "post").inc()
    return "Creating boat"


if __name__ == "__main__":
    app.run(port="5001")
    app.before_request(before_request)
    app.after_request(after_request)
