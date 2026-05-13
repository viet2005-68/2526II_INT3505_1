from flask import Flask, jsonify, request
from routes.payments import bp as payments_bp
from db import init_db
from utils.logger import logger
from utils.limiter import limiter
from prometheus_flask_exporter import PrometheusMetrics

from pybreaker import CircuitBreaker, CircuitBreakerError
import random
import time

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

# Circuit Breaker


circuit = CircuitBreaker(
    fail_max=3,
    reset_timeout=10
)

# Mock external service
def external_service_call():

    # random fail
    if random.random() > 0.4:
        time.sleep(0.1)

        raise ConnectionError(
            "External service failed"
        )

    return {
        "data": "success from external service"
    }

# Blueprint


app.register_blueprint(
    payments_bp,
    url_prefix="/api/payments"
)


# Logging
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

# Error Handlers


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


# Basic Routes
@app.route("/")
def home():
    return jsonify({
        "message": "Payment API"
    })

# =========================
# Circuit Breaker Routes
# =========================

@app.route("/api/data")
def protected_data():

    try:
        result = circuit.call(
            external_service_call
        )

        return jsonify({
            "status": "success",
            "breaker_state": circuit.current_state,
            "data": result
        })

    except CircuitBreakerError:

        return jsonify({
            "status": "fallback",
            "breaker_state": circuit.current_state,
            "message": "Service temporarily unavailable"
        }), 503

    except Exception as e:

        return jsonify({
            "status": "retry_failed",
            "breaker_state": circuit.current_state,
            "error": str(e)
        }), 500


@app.route("/api/status")
def breaker_status():

    return jsonify({
        "state": circuit.current_state,
        "failure_count": circuit.fail_counter,
        "reset_timeout": circuit.reset_timeout
    })



if __name__ == "__main__":
    app.run(debug=True)