from flask import Blueprint, request
from extensions import db, cache
from models import User, ParkingLot, ParkingSpot, Reservation
from auth import require_auth
from cache import cache_key

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/users")
@require_auth(role="admin")
def list_users():
    users = User.query.filter_by(role="user").all()
    return {"users": [{"id": u.id, "username": u.username, "email": u.email} for u in users]}


@admin_bp.post("/lots")
@require_auth(role="admin")
def create_lot():
    data = request.json or {}
    lot = ParkingLot(
        prime_location_name=data["prime_location_name"],
        price=float(data.get("price", 20.0)),
        address=data.get("address", ""),
        pin_code=data.get("pin_code", ""),
        number_of_spots=int(data.get("number_of_spots", 0)),
    )
    db.session.add(lot)
    db.session.flush()
    # bulk-create spots
    spots = [ParkingSpot(lot_id=lot.id, status="A")
             for _ in range(lot.number_of_spots)]
    db.session.add_all(spots)
    db.session.commit()
    cache.delete_memoized(get_lots_status)
    return {"id": lot.id}


@admin_bp.put("/lots/<int:lot_id>")
@require_auth(role="admin")
def update_lot(lot_id):
    data = request.json or {}
    lot = ParkingLot.query.get_or_404(lot_id)
    lot.prime_location_name = data.get(
        "prime_location_name", lot.prime_location_name)
    lot.price = float(data.get("price", lot.price))
    lot.address = data.get("address", lot.address)
    lot.pin_code = data.get("pin_code", lot.pin_code)
    new_total = int(data.get("number_of_spots", lot.number_of_spots))
    if new_total != lot.number_of_spots:
        diff = new_total - lot.number_of_spots
        if diff > 0:
            db.session.add_all(
                [ParkingSpot(lot_id=lot.id, status="A") for _ in range(diff)])
        else:
            # remove available spots first
            to_remove = ParkingSpot.query.filter_by(
                lot_id=lot.id, status="A").limit(abs(diff)).all()
            if len(to_remove) < abs(diff):
                return {"error": "not enough available spots to reduce"}, 400
            for s in to_remove:
                db.session.delete(s)
        lot.number_of_spots = new_total
    db.session.commit()
    cache.delete_memoized(get_lots_status)
    return {"ok": True}


@admin_bp.delete("/lots/<int:lot_id>")
@require_auth(role="admin")
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occ = ParkingSpot.query.filter_by(lot_id=lot.id, status="O").count()
    if occ > 0:
        return {"error": "cannot delete a lot with occupied spots"}, 400
    db.session.delete(lot)
    db.session.commit()
    cache.delete_memoized(get_lots_status)
    return {"ok": True}


@cache.memoize(timeout=60)
def get_lots_status():
    lots = ParkingLot.query.all()
    payload = []
    for lot in lots:
        total = lot.number_of_spots
        occ = ParkingSpot.query.filter_by(lot_id=lot.id, status="O").count()
        payload.append({
            "id": lot.id,
            "name": lot.prime_location_name,
            "price": lot.price,
            "total": total,
            "occupied": occ,
            "available": total - occ
        })
    return payload


@admin_bp.get("/dashboard")
@require_auth(role="admin")
def dashboard():
    return {"lots": get_lots_status()}
