from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, inspect

app = Flask(__name__)

DB_USER = "root"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = 3306
DB_DATABASE = "wedding"

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
    name = Column(String(150), server_default="")
    status = Column(String(10), server_default="pending")
    created_at = Column(TIMESTAMP())
    updated_at = Column(TIMESTAMP())


    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self):
        return '<Guest %r>' % (self.id)

class IGuest(BaseModel):
    id: int
    name: str
    updated_at: str
    
    class Config:
        orm_mode = True

@app.route("/")
def test_if_working():
    return "It is working!!!"

@app.route("/guests", methods=["GET", "POST"])
def fetch_guests() -> list[IGuest]:
    if request.method == "POST":
        id = request.form.get('id')
        status = request.form.get('status')

        if id and status:
            db = next(get_db())
            db.query(Guest).filter(
                Guest.id == id,
            ).update({
                "status": status
            })
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
def fetch_pending_guests() -> list[IGuest]:
    guests = next(get_db()).query(Guest).filter(Guest.status == "pending").all()

    guestsArr = []
    for guest in guests:
        guestsArr.append(guest.toDict()) 

    return guestsArr
