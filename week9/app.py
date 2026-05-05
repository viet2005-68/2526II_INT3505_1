from flask import Flask, jsonify
from db import init_db


app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/payment_db"

init_db(app)

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