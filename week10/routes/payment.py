from flask import Blueprint, request, jsonify
from controllers import v1, v2
from utils.limiter import limiter
from utils.logger import logger
from pybreaker import CircuitBreaker, CircuitBreakerError

# Circuit Breaker for payment routes
payment_circuit = CircuitBreaker(
    fail_max=5,
    reset_timeout=15
)


bp = Blueprint("payments", __name__)


def get_api_version():
    version = request.args.get("v")

    if version:
        return version.replace("v", "")

    return "2"


@bp.route("/", methods=["POST"])
@limiter.limit("10 per minute")
def create_dispatch():
    version = get_api_version()
    
    try:
        logger.info({
            "event": "POST_create_dispatch",
            "version": version,
            "status": "processing",
            "breaker_state": payment_circuit.current_state
        })
        
        # Use circuit breaker to protect POST request
        if version == "1":
            result = payment_circuit.call(v1.create_payment)
        elif version == "2":
            result = payment_circuit.call(v2.create_payment)
        else:
            logger.error({
                "event": "POST_create_dispatch",
                "error_type": "UnsupportedVersionError",
                "version": version,
                "status": "failed"
            })
            return jsonify({
                "error": "Unsupported API version"
            }), 400
        
        logger.info({
            "event": "POST_create_dispatch",
            "version": version,
            "status": "completed",
            "breaker_state": payment_circuit.current_state
        })
        
        return result
        
    except CircuitBreakerError as e:
        logger.error({
            "event": "POST_create_dispatch_error",
            "error_type": "CircuitBreakerOpen",
            "version": version,
            "error": str(e),
            "breaker_state": payment_circuit.current_state,
            "failure_count": payment_circuit.fail_counter
        })
        return jsonify({
            "error": "Payment service temporarily unavailable",
            "breaker_state": payment_circuit.current_state
        }), 503
    
    except Exception as e:
        import traceback
        logger.error({
            "event": "POST_create_dispatch_error",
            "error_type": type(e).__name__,
            "version": version,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "breaker_state": payment_circuit.current_state
        })
        return jsonify({
            "error": str(e)
        }), 500


@bp.route("/", methods=["GET"])
@limiter.limit("30 per minute")
def list_dispatch():
    version = get_api_version()

    if version == "1":
        return v1.get_payments()

    elif version == "2":
        return v2.get_payments()

    return jsonify({
        "error": "Unsupported API version"
    }), 400


@bp.route("/<int:id>", methods=["GET"])
@limiter.limit("30 per minute")
def get_dispatch(id):
    version = get_api_version()

    if version == "1":
        return v1.get_payment(id)

    elif version == "2":
        return v2.get_payment(id)

    return jsonify({
        "error": "Unsupported API version"
    }), 400


@bp.route("/<int:id>", methods=["PUT"])
def update_dispatch(id):
    version = get_api_version()

    if version == "1":
        return v1.update_payment(id)

    elif version == "2":
        return v2.update_payment(id)

    return jsonify({
        "error": "Unsupported API version"
    }), 400


@bp.route("/<int:id>", methods=["DELETE"])
@limiter.limit("5 per minute")
def delete_dispatch(id):
    version = get_api_version()

    if version == "1":
        return v1.delete_payment(id)

    elif version == "2":
        return v2.delete_payment(id)

    return jsonify({
        "error": "Unsupported API version"
    }), 400


# Circuit Breaker Status Endpoint
@bp.route("/status/breaker", methods=["GET"])
def payment_breaker_status():
    """Check circuit breaker status for payment routes"""
    logger.info({
        "event": "circuit_breaker_status_check",
        "breaker_state": payment_circuit.current_state
    })
    
    return jsonify({
        "circuit_breaker": {
            "state": payment_circuit.current_state,
            "failure_count": payment_circuit.fail_counter,
            "reset_timeout": payment_circuit.reset_timeout,
            "fail_max": payment_circuit.fail_max
        }
    }), 200