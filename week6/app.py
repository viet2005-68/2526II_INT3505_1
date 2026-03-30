from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.config["JWT_ACCESS_SECRET"] = os.getenv("JWT_ACCESS_SECRET")
app.config["JWT_REFRESH_SECRET"] = os.getenv("JWT_REFRESH_SECRET")
app.config["ACCESS_MIN"] = os.getenv("ACCESS_MIN")
app.config["REFRESH_DAYS"] = os.getenv("REFRESH_DAYS")

USERS = {}
@app.route("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True, port =8003)