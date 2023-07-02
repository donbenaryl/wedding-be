from flask import Flask, request, Blueprint

app = Flask(__name__)
    
auth_page = Blueprint("auth", __name__, url_prefix="/auth")

@auth_page.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return "this is a post"
    else:
        return "this is a get"
