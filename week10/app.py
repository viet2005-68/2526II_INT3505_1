from flask import Flask, jsonify, request
from routes.payment import bp as payments_bp
from db import init_db
from utils.logger import logger
from utils.limiter import limiter
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import generate_latest, REGISTRY, CollectorRegistry
from utils.waf import waf_check
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

@app.before_request
def security_layer():

    blocked = waf_check()

    if blocked:
        return blocked

# Logging
@app.before_request
def log_request():
    # Capture body for logging
    body = None
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            body = request.get_json(silent=True)
        except:
            body = "Could not parse JSON"
    
    logger.info({
        "event": "incoming_request",
        "method": request.method,
        "path": request.path,
        "args": request.args.to_dict(),
        "body": body
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
    import traceback
    logger.error({
        "event": "internal_error",
        "error_type": type(e).__name__,
        "error": str(e),
        "path": request.path,
        "method": request.method,
        "traceback": traceback.format_exc(),
        "body": request.get_json(silent=True),
        "args": request.args.to_dict()
    })

    return jsonify({
        "error": "Internal Server Error"
    }), 500


@app.errorhandler(400)
def handle_bad_request(e):
    import traceback
    logger.warning({
        "event": "bad_request_error",
        "error_type": "BadRequest",
        "error": str(e),
        "path": request.path,
        "method": request.method,
        "description": str(e.description)
    })
    return jsonify({
        "error": "Bad request",
        "message": str(e.description)
    }), 400


@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning({
        "event": "rate_limit_exceeded",
        "error_type": "RateLimitError",
        "path": request.path,
        "method": request.method,
        "message": str(e.description),
        "status": 429
    })
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


# ===============================
# Prometheus Metrics Endpoint
# ===============================

@app.route("/metrics")
def metrics_endpoint():
    """
    Prometheus metrics endpoint
    Visit: http://localhost:5000/metrics
    View metrics for:
    - Flask request counts & latency
    - HTTP status codes
    - Payment API calls
    """
    logger.info({
        "event": "metrics_requested",
        "status": "serving_metrics"
    })
    # Generate metrics from prometheus client registry
    return generate_latest(REGISTRY)


if __name__ == "__main__":
    app.run(debug=True)