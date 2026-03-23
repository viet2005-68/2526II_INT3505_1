from flask import Flask
from database import db

from route.book import books_bp
from route.loans import loans_bp
from route.user import users_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(books_bp)
app.register_blueprint(loans_bp)
app.register_blueprint(users_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=8003)
