from datetime import datetime
from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # "admin" or "user"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservations = db.relationship("Reservation", backref="user", lazy=True)


class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False, default=20.0)  # per hour
    address = db.Column(db.String(255))
    pin_code = db.Column(db.String(10))
    number_of_spots = db.Column(db.Integer, nullable=False, default=0)
    spots = db.relationship("ParkingSpot", backref="lot",
                            lazy=True, cascade="all, delete-orphan")


class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey(
        "parking_lot.id"), nullable=False)
    status = db.Column(db.String(1), default="A")  # A available, O occupied
    reservations = db.relationship("Reservation", backref="spot", lazy=True)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey(
        "parking_spot.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    remarks = db.Column(db.String(255), nullable=True)
