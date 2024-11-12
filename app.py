from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from sqlalchemy import Column, Integer, String, TIMESTAMP, inspect, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
import cryptocode
from jose import JWTError, jwt

app = Flask(__name__)
# CORS(app)
# cors = CORS(app, resources={r"/api": {"origins": "http://localhost:4200"}})
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})
# app = CORS(app, resources={r"/api/*": {"origins": ["http://localhost:4200", "http://www.domain2.com"]}})

# cors = CORS(app, origins=['http://localhost:4200', 'http://192.168.1.163:4200'])
# app.config['CORS_HEADERS'] = 'Content-Type'

DB_USER = "root"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = 3306
DB_DATABASE = "wedding"

key = "0x66dFA4b56678B6EdE0ab2765804EeB009dc0EE47"
SECRET_KEY = "12da3c99a9c42c33347b67e452af5e8b9bad81bc4fbfb777af9749cbc6e5399d"

engine=create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}', pool_size=20, max_overflow=0)
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

class Guest(Base):
    __tablename__ = 'w_guests'
    id = Column(Integer(), primary_key = True)
    guest_uuid = Column(String(36), server_default="")
    name = Column(String(150), server_default="")
    contact_number = Column(String(20), server_default="")
    status = Column(String(10), server_default="pending")
    link = Column(String(500), server_default="")
    created_at = Column(TIMESTAMP())
    updated_at = Column(TIMESTAMP())


    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self):
        return '<Guest %r>' % (self.id)

class User(Base):
    __tablename__ = 'w_users'
    id = Column(Integer(), primary_key = True)
    email = Column(String(150), server_default="")
    password = Column(String(150), server_default="pending")
    created_at = Column(TIMESTAMP())
    updated_at = Column(TIMESTAMP())


    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self):
        return '<User %r>' % (self.id)

class Faq(Base):
    __tablename__ = 'w_faq'
    id = Column(Integer(), primary_key = True)
    question = Column(String(2000), server_default="")
    answer = Column(String(5000), server_default="")


    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self):
        return '<Faq %r>' % (self.id)
    

@app.route("/")
def test_if_working():
    return "It is working!!!"

@app.route("/guests", methods=["GET", "POST"])
def fetch_add_guests():
    if request.method == "POST":
        name = request.form.get('name')

        if name:
            db = next(get_db())

            user = db.query(Guest).filter(Guest.name == name).first()

            if user:
                return ('User already exists!', 409)
            
            db.add(Guest(**{
                "created_at": datetime.now(),
                "name": name
            }))
            db.commit()


            return ('', 204)

        return ('Malformed Data!', 422)
    else:
        guests = next(get_db()).query(Guest).all()

        guestsArr = []
        for guest in guests:
            guestsArr.append(guest.toDict()) 

        return guestsArr

@app.route("/guests/pending", methods=["GET"])
def fetch_pending_guests():
    guests = next(get_db()).query(Guest).filter(Guest.status == "pending").all()

    guestsArr = []
    for guest in guests:
        guestsArr.append(guest.toDict()) 

    return guestsArr


@app.route("/guests/status", methods=["POST"])
def update_guest_status():
    data = request.json

    if data["id"] and data["status"]:
        db = next(get_db())
        db.query(Guest).filter(
            Guest.id == data["id"],
        ).update({
            "status": data["status"],
            "contact_number": data["contact_number"] if "contact_number" in data else ""
        })
        db.commit()


        return ('', 204)

    return ('Malformed Data!', 422)


@app.route("/guests/upsert", methods=["POST"])
def upsert_guests():
    data = request.json

    # print(data)
    # return ('', 204)

    if "toUpdate" in data and "toAdd" in data and "toDelete" in data:
        db = next(get_db())

        for id in data["toDelete"]:
            db.query(Guest).filter(Guest.id == id).delete()
        
        for guest in data["toAdd"]:
            user = db.query(Guest).filter(Guest.name == guest["name"]).first()

            if user == None:
                db.add(Guest(**dict(guest)))

        for guest in data["toUpdate"]:
            db.query(Guest).filter(Guest.id == guest["id"]).update({
                "status": guest["status"],
                "name": guest["name"],
                "contact_number": guest["contact_number"]
            })

        db.commit()

        return ('', 204)

    return ('Malformed Data!', 422)


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    temporary_accounts = [
        {
            "email": "don@email.com",
            "password": "P@ssw0rd123!"
        }
    ]

    if data and data['email'] and data['password']:
        user = [d for d in temporary_accounts if d['email'] == data["email"]]

        if user:
            if data["password"] == user[0]["password"]:
                to_encode = {
                    "email": data["email"],
                    "exp": datetime.utcnow() + timedelta(minutes = 0)
                }

                encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
                return make_response(jsonify({
                    "token": encoded_jwt
                }), 200)
            
        return make_response(jsonify({
                    "msg": 'Invalid username or password'
                }), 401)
    
    return make_response(jsonify({
                    "msg": 'Malformed Data!'
                }), 400)


def login_backup():
    data = request.json

    # USED FOR CREATING PASSWORD
    encoded = cryptocode.encrypt("password", key)
    print(encoded)
    ## DECODING
    # decoded = cryptocode.decrypt(encoded, key)

    if data and data['email'] and data['password']:
        db = next(get_db())
        user = db.query(User).filter(User.email == data['email']).first()

        if user:
            encrypted_password = user.password
            decoded_password = cryptocode.decrypt(encrypted_password, key)

            if decoded_password == data['password']:
                to_encode = {
                    "email": data["email"],
                    "exp": datetime.utcnow() + timedelta(minutes = 0)
                }

                encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
                return make_response(jsonify({
                    "token": encoded_jwt
                }), 200)
            
        return make_response(jsonify({
                    "msg": 'Invalid username or password'
                }), 401)
    
    return make_response(jsonify({
                    "msg": 'Malformed Data!'
                }), 400)


@app.route("/faq", methods=["GET"])
def fetch_faq():
    faq = next(get_db()).query(Faq).all()

    faqArr = []
    for faq in faq:
        faqArr.append(faq.toDict()) 

    return faqArr
