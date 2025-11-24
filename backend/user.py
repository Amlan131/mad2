from flask import Blueprint, request, jsonify
from extensions import db, cache
from models import ParkingLot, ParkingSpot, Reservation
from auth import require_auth
from tasks import export_user_csv
from datetime import datetime

user_bp = Blueprint("user", __name__)


@user_bp.get("/lots")
@require_auth()
def available_lots():
    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        total = lot.number_of_spots
        occ = ParkingSpot.query.filter_by(lot_id=lot.id, status="O").count()
        data.append({
            "id": lot.id,
            "name": lot.prime_location_name,
            "price": lot.price,
            "total": total,
            "available": total - occ
        })
    return {"lots": data}


@user_bp.post("/book")
@require_auth()
def book():
    data = request.json or {}
    lot_id = int(data["lot_id"])
    lot = ParkingLot.query.get_or_404(lot_id)
    spot = ParkingSpot.query.filter_by(
        lot_id=lot.id, status="A").order_by(ParkingSpot.id.asc()).first()
    if not spot:
        return {"error": "no available spot"}, 400
    spot.status = "O"
    res = Reservation(spot_id=spot.id, user_id=request.user.id,
                      parking_timestamp=datetime.utcnow())
    db.session.add(res)
    db.session.commit()
    return {"reservation_id": res.id, "spot_id": spot.id}


@user_bp.post("/release")
@require_auth()
def release():
    data = request.json or {}
    res_id = int(data["reservation_id"])
    res = Reservation.query.get_or_404(res_id)
    if res.user_id != request.user.id:
        return {"error": "forbidden"}, 403
    if res.leaving_timestamp:
        return {"error": "already released"}, 400
    res.leaving_timestamp = datetime.utcnow()
    hours = max(
        1, int((res.leaving_timestamp - res.parking_timestamp).total_seconds() // 3600))
    lot_price = res.spot.lot.price
    res.parking_cost = hours * lot_price
    res.spot.status = "A"
    db.session.commit()
    return {"cost": res.parking_cost, "hours": hours}


@user_bp.get("/reservations")
@require_auth()
def my_reservations():
    rows = Reservation.query.filter_by(
        user_id=request.user.id).order_by(Reservation.id.desc()).all()
    return {"rows": [{
        "id": r.id,
        "spot_id": r.spot_id,
        "lot_id": r.spot.lot_id,
        "parking_in": r.parking_timestamp.isoformat(),
        "parking_out": r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
        "cost": r.parking_cost
    } for r in rows]}


@user_bp.post("/export_csv")
@require_auth()
def export_csv():
    task = export_user_csv.delay(request.user.id)
    return {"task_id": task.id}


@user_bp.get("/export_status/<task_id>")
@require_auth()
def export_status(task_id):
    from app import celery_app
    async_res = celery_app.AsyncResult(task_id)
    if async_res.successful():
        res = async_res.get()
        return {"ready": True, "filename": res["filename"], "content": res["content"]}
    return {"ready": False, "state": async_res.state}
