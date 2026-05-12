from flask import Flask, jsonify
from routes.payments import bp as payments_bp
from db import init_db

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/payment_db"

init_db(app)

app.register_blueprint(
    payments_bp,
    url_prefix="/api/payments"
)

@app.route("/")
def home():
    return jsonify({
        "message": "Payment API"
    })


if __name__ == "__main__":
    app.run(debug=True)