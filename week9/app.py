from flask import Flask, jsonify
from db import init_db
from router import v1, v2, payment

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/payment_db"

init_db(app)
app.register_blueprint(v1.v1_bp, url_prefix='/api/v1/payments')
app.register_blueprint(v2.bp, url_prefix='/api/v2/payments')
app.register_blueprint(payment.bp, url_prefix='/api/payments')

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to Payment API System",
        "versions": [
            {"version": "v1", "status": "Deprecated", "docs": "/api/v1/payments"}
        ]
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)