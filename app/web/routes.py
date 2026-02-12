from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import re
import secrets
from functools import wraps

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.db import db
from app.models import Company, PasswordResetToken, ScheduledPost, Store, User
from app.services.support_service import SAFE_FALLBACK

web_bp = Blueprint("web", __name__)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:180] or f"company-{secrets.token_hex(4)}"


def _parse_datetime_local(value: str) -> datetime | None:
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M")
        return dt.replace(tzinfo=UTC)
    except ValueError:
        return None


def _get_store_for_company(store_id: int, company_id: int) -> Store | None:
    return Store.query.filter_by(id=store_id, company_id=company_id).first()


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("web.login"))
        return view_func(*args, **kwargs)

    return wrapper


@web_bp.get("/")
def home():
    return render_template("home.html")


@web_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        store_name = request.form.get("store_name", "").strip()
        platform = request.form.get("platform", "").strip()
        store_url = request.form.get("store_url", "").strip()
        external_api_token = request.form.get("external_api_token", "").strip()
        external_api_secret = request.form.get("external_api_secret", "").strip()

        required = [company_name, name, email, password, store_name, platform, store_url, external_api_token, external_api_secret]
        if any(not item for item in required):
            flash("All fields are required.", "error")
            return render_template("auth/register.html")
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("auth/register.html")
        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "error")
            return render_template("auth/register.html")

        base_slug = _slugify(company_name)
        slug = base_slug
        counter = 1
        while Company.query.filter_by(slug=slug).first() is not None:
            counter += 1
            slug = f"{base_slug}-{counter}"

        company = Company(name=company_name, slug=slug)
        db.session.add(company)
        db.session.flush()

        user = User(company_id=company.id, name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)

        store = Store(
            company_id=company.id,
            name=store_name,
            platform=platform,
            store_url=store_url,
            external_api_token=external_api_token,
            external_api_secret=external_api_secret,
            internal_api_key=Store.generate_internal_api_key(),
            internal_webhook_token=Store.generate_webhook_token(),
            status="connected",
        )
        db.session.add(store)

        db.session.commit()
        flash("Account and first store created successfully. Please login.", "success")
        return redirect(url_for("web.login"))

    return render_template("auth/register.html")


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user is None or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        company = Company.query.get(user.company_id)
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["company_id"] = user.company_id
        session["company_name"] = company.name if company else "Unknown Company"
        flash("Welcome back!", "success")
        return redirect(url_for("web.dashboard"))

    return render_template("auth/login.html")


@web_bp.get("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("web.login"))


@web_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_link = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = PasswordResetToken.generate(user.id)
            db.session.add(token)
            db.session.commit()
            reset_link = url_for("web.reset_password", token=token.token, _external=True)
            flash("Reset link generated. In production this is emailed to user.", "success")
        else:
            flash("If the email exists, reset steps are generated.", "info")

    return render_template("auth/forgot_password.html", reset_link=reset_link)


@web_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    if reset_token is None or not reset_token.is_valid():
        flash("Invalid or expired reset token.", "error")
        return redirect(url_for("web.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("auth/reset_password.html", token=token)

        user = User.query.get(reset_token.user_id)
        if user is None:
            flash("User no longer exists.", "error")
            return redirect(url_for("web.forgot_password"))

        user.password_hash = generate_password_hash(password)
        db.session.delete(reset_token)
        db.session.commit()
        flash("Password updated successfully. Please login.", "success")
        return redirect(url_for("web.login"))

    return render_template("auth/reset_password.html", token=token)


@web_bp.post("/stores/add")
@login_required
def add_store():
    company_id = session["company_id"]
    store_name = request.form.get("store_name", "").strip()
    platform = request.form.get("platform", "").strip()
    store_url = request.form.get("store_url", "").strip()
    external_api_token = request.form.get("external_api_token", "").strip()
    external_api_secret = request.form.get("external_api_secret", "").strip()

    required = [store_name, platform, store_url, external_api_token, external_api_secret]
    if any(not item for item in required):
        flash("All store fields are required.", "error")
        return redirect(url_for("web.dashboard"))

    store = Store(
        company_id=company_id,
        name=store_name,
        platform=platform,
        store_url=store_url,
        external_api_token=external_api_token,
        external_api_secret=external_api_secret,
        internal_api_key=Store.generate_internal_api_key(),
        internal_webhook_token=Store.generate_webhook_token(),
        status="connected",
    )
    db.session.add(store)
    db.session.commit()
    flash("New store connected successfully.", "success")
    return redirect(url_for("web.dashboard"))


@web_bp.post("/stores/<int:store_id>/connect-x")
@login_required
def connect_x_integration(store_id: int):
    store = _get_store_for_company(store_id, session["company_id"])
    if store is None:
        flash("Store not found.", "error")
        return redirect(url_for("web.dashboard"))

    x_handle = request.form.get("x_handle", "").strip()
    x_bearer_token = request.form.get("x_bearer_token", "").strip()

    if not x_handle or not x_bearer_token:
        flash("X handle and bearer token are required.", "error")
        return redirect(url_for("web.store_dashboard", store_id=store_id))

    store.x_handle = x_handle
    store.x_bearer_token = x_bearer_token
    db.session.commit()
    flash("X integration saved successfully.", "success")
    return redirect(url_for("web.store_dashboard", store_id=store_id))


@web_bp.post("/stores/<int:store_id>/publishing/schedule")
@login_required
def schedule_post(store_id: int):
    store = _get_store_for_company(store_id, session["company_id"])
    if store is None:
        flash("Store not found.", "error")
        return redirect(url_for("web.dashboard"))

    content = request.form.get("content", "").strip()
    publish_at_raw = request.form.get("publish_at", "").strip()

    if not content:
        flash("Post content is required.", "error")
        return redirect(url_for("web.store_dashboard", store_id=store_id))
    if len(content) > 280:
        flash("X content must be 280 characters or fewer.", "error")
        return redirect(url_for("web.store_dashboard", store_id=store_id))

    publish_at = _parse_datetime_local(publish_at_raw)
    if publish_at is None:
        flash("Invalid schedule date/time.", "error")
        return redirect(url_for("web.store_dashboard", store_id=store_id))

    post = ScheduledPost(company_id=session["company_id"], store_id=store.id, content=content, publish_at=publish_at, status="scheduled")
    db.session.add(post)
    db.session.commit()
    flash("Post scheduled successfully.", "success")
    return redirect(url_for("web.store_dashboard", store_id=store_id))


@web_bp.post("/stores/<int:store_id>/publishing/run-pending")
@login_required
def run_pending_posts(store_id: int):
    store = _get_store_for_company(store_id, session["company_id"])
    if store is None:
        flash("Store not found.", "error")
        return redirect(url_for("web.dashboard"))
    if not store.x_bearer_token:
        flash("Please connect X integration first.", "error")
        return redirect(url_for("web.store_dashboard", store_id=store_id))

    now_utc = datetime.now(UTC)
    pending = ScheduledPost.query.filter(
        ScheduledPost.company_id == session["company_id"],
        ScheduledPost.store_id == store.id,
        ScheduledPost.status == "scheduled",
        ScheduledPost.publish_at <= now_utc,
    ).all()

    if not pending:
        flash("No pending scheduled posts right now.", "info")
        return redirect(url_for("web.store_dashboard", store_id=store_id))

    client = current_app.config["SUPPORT_SERVICE"].n8n_client
    posted = 0
    failed = 0

    for post in pending:
        payload = {
            "company_id": session["company_id"],
            "company_name": session.get("company_name", "Unknown Company"),
            "store_id": store.id,
            "store_name": store.name,
            "store_url": store.store_url,
            "internal_api_key": store.internal_api_key,
            "internal_webhook_token": store.internal_webhook_token,
            "x_handle": store.x_handle,
            "x_bearer_token": store.x_bearer_token,
            "text": post.content,
            "scheduled_post_id": post.id,
        }

        try:
            result = asyncio.run(client.publish_x_post(payload))
            post.status = "posted"
            post.external_post_id = str(result.get("tweet_id", ""))
            posted += 1
        except RuntimeError:
            post.status = "failed"
            post.external_post_id = SAFE_FALLBACK.get("reply", "")[:120]
            failed += 1

    db.session.commit()
    flash(f"Publishing finished. posted={posted}, failed={failed}", "success")
    return redirect(url_for("web.store_dashboard", store_id=store_id))


@web_bp.post("/integrations/simulate-ticket")
@login_required
def simulate_ticket():
    message = request.get_json(silent=True, force=True) or {}
    customer_message = message.get("message", "Order #1001 has not arrived yet.")

    webhook_path = f"/webhooks/{session['company_id']}/support/{secrets.token_hex(8)}"
    return jsonify(
        {
            "company": session.get("company_name"),
            "simulation": {
                "incoming_store_event": {
                    "type": "customer_support_created",
                    "payload": {
                        "customer_id": "cust_demo_001",
                        "message": customer_message,
                    },
                    "target": webhook_path,
                },
                "next_step": "Send payload to /api/v1/support then forward response to CRM/helpdesk.",
            },
            "n8n_webhook_url": current_app.config["SETTINGS"].n8n_webhook_url,
        }
    )


@web_bp.get("/dashboard")
@login_required
def dashboard():
    stores = Store.query.filter_by(company_id=session["company_id"]).order_by(Store.created_at.desc()).all()
    return render_template("dashboard/index.html", user_name=session.get("user_name", "User"), company_name=session.get("company_name", "Company"), stores=stores)


@web_bp.get("/dashboard/store/<int:store_id>")
@login_required
def store_dashboard(store_id: int):
    store = _get_store_for_company(store_id, session["company_id"])
    if store is None:
        flash("Store not found.", "error")
        return redirect(url_for("web.dashboard"))

    posts = ScheduledPost.query.filter_by(company_id=session["company_id"], store_id=store.id).order_by(ScheduledPost.created_at.desc()).limit(20).all()
    return render_template(
        "dashboard/store.html",
        user_name=session.get("user_name", "User"),
        company_name=session.get("company_name", "Company"),
        store=store,
        posts=posts,
    )
