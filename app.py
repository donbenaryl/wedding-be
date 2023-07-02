from flask import Flask
from markupsafe import escape
from src.app.auth.routes import auth_page
from src.app.guests.routes import guests_page

app = Flask(__name__)

app.register_blueprint(auth_page)
app.register_blueprint(guests_page)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
