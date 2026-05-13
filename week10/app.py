from flask import Flask, jsonify, request
from routes.payments import bp as payments_bp
from db import init_db
from utils.logger import logger
from utils.limiter import limiter
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/payment_db"

init_db(app)

limiter.init_app(app)

metrics = PrometheusMetrics(app)

metrics.info(
    "app_info",
    "Payment API Monitoring",
    version="1.0.0"
)

app.register_blueprint(
    payments_bp,
    url_prefix="/api/payments"
)

@app.before_request
def log_request():
    logger.info({
        "event": "incoming_request",
        "method": request.method,
        "path": request.path,
        "args": request.args.to_dict(),
        "body": request.get_json(silent=True)
    })


@app.after_request
def log_response(response):
    logger.info({
        "event": "response_sent",
        "status": response.status_code,
        "path": request.path
    })

    return response


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error({
        "event": "internal_error",
        "error": str(e),
        "path": request.path
    })

    return jsonify({
        "error": "Internal Server Error"
    }), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": str(e.description)
    }), 429


@app.route("/")
def home():
    return jsonify({
        "message": "Payment API"
    })


if __name__ == "__main__":
    app.run(debug=True)