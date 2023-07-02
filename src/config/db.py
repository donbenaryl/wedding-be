from flask_mysqldb import MySQL
import yaml

def init(app):
    app.config['MYSQL_HOST'] = "localhost"
    app.config['MYSQL_USER'] = "root"
    app.config['MYSQL_PASSWORD'] = ""
    app.config['MYSQL_DB'] = "wedding"

    return MySQL(app)