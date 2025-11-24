# tasks.py
from app import celery_app  # after app created
from chat_webhook import post_chat
from email_utils import send_email
from models import User, Reservation, ParkingLot, ParkingSpot
from extensions import db
from celery import Celery
from datetime import datetime, timedelta
from flask import current_app
from dateutil.relativedelta import relativedelta


def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        broker=flask_app.config["CELERY"]["broker_url"],
        backend=flask_app.config["CELERY"]["result_backend"],
    )
    celery.conf.update(flask_app.config["CELERY"])
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    # Beat schedule: daily reminder at fixed time, monthly report on day 1
    ist_hour = flask_app.config.get("REMINDER_HOUR_IST", 18)

    celery.conf.beat_schedule = {
        "daily-reminders": {
            "task": "tasks.send_daily_reminders",
            "schedule": timedelta(days=1),
        },
        "monthly-reports": {
            "task": "tasks.generate_monthly_reports",
            "schedule": timedelta(days=1),
        },
    }
    return celery


# Actual tasks


def _today_ist():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


def _first_of_month(dt):
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


@celery_app.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    # Users who registered but never booked OR not visited recently
    users = User.query.filter_by(role="user").all()
    for u in users:
        last_res = (
            Reservation.query.filter_by(user_id=u.id)
            .order_by(Reservation.parking_timestamp.desc())
            .first()
        )
        should_notify = last_res is None
        if last_res:
            delta = _today_ist() - (last_res.parking_timestamp or _today_ist())
            if delta.days >= 7:
                should_notify = True
        if should_notify:
            if current_app.config.get("GOOGLE_CHAT_WEBHOOK"):
                post_chat(
                    f"Hi {u.username}, parking spots are available. Book if needed today!")
            if current_app.config.get("FROM_EMAIL") and u.email:
                send_email(
                    to=u.email,
                    subject="Parking Reminder",
                    html=f"<p>Hi {u.username}, remember to book a parking spot if needed today.</p>",
                )
    return {"status": "ok", "count": len(users)}


@celery_app.task(name="tasks.generate_monthly_reports")
def generate_monthly_reports():
    now = _today_ist()
    if now.day != 1:
        return {"skipped": True}
    start = _first_of_month(now - relativedelta(months=1))
    end = _first_of_month(now)
    users = User.query.filter_by(role="user").all()
    for u in users:
        qs = Reservation.query.filter(
            Reservation.user_id == u.id,
            Reservation.parking_timestamp >= start,
            Reservation.parking_timestamp < end,
        ).all()
        total = sum([r.parking_cost or 0 for r in qs])
        most_lot = None
        if qs:
            by_lot = {}
            for r in qs:
                by_lot[r.spot.lot.id] = by_lot.get(r.spot.lot.id, 0) + 1
            lot_id = max(by_lot, key=by_lot.get)
            most_lot = ParkingLot.query.get(lot_id).prime_location_name
        html = f"""
        <h3>Monthly Parking Report</h3>
        <p>User: {u.username}</p>
        <p>Period: {start.date()} to {end.date()}</p>
        <p>Bookings: {len(qs)}</p>
        <p>Most used lot: {most_lot or 'N/A'}</p>
        <p>Amount spent: ₹{total:.2f}</p>
        """
        if current_app.config.get("FROM_EMAIL") and u.email:
            send_email(
                to=u.email, subject="Your Monthly Parking Report", html=html)
    return {"status": "done", "users": len(users)}


@celery_app.task(name="tasks.export_user_csv")
def export_user_csv(user_id):
    import io
    import csv
    from flask import url_for

    user = User.query.get(user_id)
    if not user:
        return {"error": "user not found"}

    rows = Reservation.query.filter_by(
        user_id=user_id).order_by(Reservation.id.desc()).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["reservation_id", "spot_id", "lot_id",
                    "parking_in", "parking_out", "cost", "remarks"])
    for r in rows:
        writer.writerow([
            r.id,
            r.spot_id,
            r.spot.lot_id,
            r.parking_timestamp,
            r.leaving_timestamp,
            r.parking_cost or 0,
            r.remarks or "",
        ])
    csv_text = buf.getvalue()

    # For demo, return as string; in production, store to S3 or local file and notify with link
    if current_app.config.get("GOOGLE_CHAT_WEBHOOK"):
        post_chat(
            f"Your CSV export is ready for user {user.username} ({len(rows)} rows).")
    return {"filename": f"parking_{user.username}.csv", "content": csv_text}
