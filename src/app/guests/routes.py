from flask import Flask, request, Blueprint

app = Flask(__name__)
    
guests_page = Blueprint("guests", __name__, url_prefix="/guests")

@guests_page.route("/", methods=["GET"])
def fetch_guests():
    return 'Don'
