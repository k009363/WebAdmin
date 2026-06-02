"""Subscription management endpoints."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.db import get_db, to_json
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from middleware.rbac import jwt_required_with_role
from middleware.permissions import get_admin_visibility_filter

subscriptions_bp = Blueprint("subscriptions", __name__)


@subscriptions_bp.route("/domains/<domain_id>/subscribe", methods=["POST"])
@jwt_required()
def create_subscription(domain_id):
    """Create or update subscription for a domain."""
    try:
        data = request.get_json() or {}
        subscription_type = data.get("subscription_type", "none").lower()
        price = data.get("price")

        # Validate subscription type
        if subscription_type not in ["monthly", "yearly", "none"]:
            return jsonify({"error": "Invalid subscription type"}), 400

        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        # Find domain
        domain = db.domains.find_one({"_id": ObjectId(domain_id)})
        if not domain:
            return jsonify({"error": "Domain not found"}), 404

        # Permission check: regular admin can only manage their own domains
        if claims.get("role") != "super_admin" and domain.get("admin_id") != admin_id:
            return jsonify({"error": "You can only manage your own domains"}), 403

        # Calculate end date
        now = datetime.now(timezone.utc)
        if subscription_type == "monthly":
            end_date = now + timedelta(days=30)
        elif subscription_type == "yearly":
            end_date = now + timedelta(days=365)
        else:  # "none" (trial)
            end_date = now + timedelta(days=30)

        # Update domain subscription
        update_data = {
            "subscription": {
                "type": subscription_type,
                "start_date": now,
                "end_date": end_date,
                "price": price,
                "is_active": True
            },
            "updated_at": now
        }

        update_data["subscription_expiry_notified"] = False
        update_data["subscription_expiry_warning_sent"] = False
        db.domains.update_one(
            {"_id": ObjectId(domain_id)},
            {"$set": update_data}
        )

        # Create subscription record in subscriptions collection
        duration_days = 30 if subscription_type in ["monthly", "none"] else 365
        payment_status = "free_trial" if subscription_type == "none" else "completed"

        subscription_record = {
            "domain_id": ObjectId(domain_id),
            "domain_full_key": domain.get("full_key"),
            "admin_id": admin_id,
            "subscription_type": subscription_type,
            "price": price,
            "start_date": now,
            "end_date": end_date,
            "duration_days": duration_days,
            "payment_status": payment_status,
            "created_at": now,
            "updated_at": now,
        }

        result = db.subscriptions.insert_one(subscription_record)
        subscription_record["_id"] = result.inserted_id

        # Notify super admin of renewal
        try:
            from routes.notifications import notify_subscription_renewed
            updated_for_notif = db.domains.find_one({"_id": ObjectId(domain_id)})
            notify_subscription_renewed(db, updated_for_notif, admin_id, subscription_type, price)
        except Exception:
            pass

        # Return updated domain
        updated_domain = db.domains.find_one({"_id": ObjectId(domain_id)})

        return jsonify({
            "message": f"Subscription activated: {subscription_type.capitalize()}",
            "domain": to_json(updated_domain),
            "subscription": to_json(subscription_record)
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@subscriptions_bp.route("", methods=["GET"])
@jwt_required()
def list_subscriptions():
    """List subscription history (with optional domain_id filter)."""
    try:
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        domain_id = request.args.get("domain_id")

        # Build query
        query = {}
        if domain_id:
            query["domain_id"] = ObjectId(domain_id)

            # Permission check: can only view own domain subscriptions
            domain = db.domains.find_one({"_id": ObjectId(domain_id)})
            if not domain:
                return jsonify({"error": "Domain not found"}), 404

            if claims.get("role") != "super_admin" and domain.get("admin_id") != admin_id:
                return jsonify({"error": "You can only view your own domain subscriptions"}), 403

        # Super admin sees all, regular admin sees only their own
        if claims.get("role") != "super_admin":
            query["admin_id"] = admin_id

        subscriptions = list(db.subscriptions.find(query).sort("created_at", -1))

        return jsonify(to_json(subscriptions)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@subscriptions_bp.route("/stats", methods=["GET"])
@jwt_required_with_role("super_admin")
def subscription_stats():
    """Subscription statistics (super_admin only)."""
    try:
        db = get_db()

        total_subscriptions = db.subscriptions.count_documents({})
        active_subscriptions = db.subscriptions.count_documents(
            {"end_date": {"$gt": datetime.now(timezone.utc)}}
        )
        expired_subscriptions = db.subscriptions.count_documents(
            {"end_date": {"$lte": datetime.now(timezone.utc)}}
        )

        # Count by type
        subscription_types = {}
        for sub_type in ["monthly", "yearly", "none"]:
            subscription_types[sub_type] = db.subscriptions.count_documents(
                {"subscription_type": sub_type}
            )

        # Total revenue (sum of prices where payment_status is completed)
        pipeline = [
            {"$match": {"payment_status": "completed", "price": {"$ne": None}}},
            {"$group": {"_id": None, "total": {"$sum": "$price"}}}
        ]
        revenue_result = list(db.subscriptions.aggregate(pipeline))
        total_revenue = revenue_result[0]["total"] if revenue_result else 0

        return jsonify({
            "total": total_subscriptions,
            "active": active_subscriptions,
            "expired": expired_subscriptions,
            "by_type": subscription_types,
            "total_revenue": total_revenue,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@subscriptions_bp.route("/reports", methods=["GET"])
@jwt_required()
def get_reports():
    """Get subscription reports with filtering support."""
    try:
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        # Get filter parameters
        domain_id = request.args.get("domain_id")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        # Build query
        query = {}

        # Date range filter
        if start_date_str or end_date_str:
            date_filter = {}
            if start_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                    date_filter["$gte"] = start_date
                except:
                    pass
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    date_filter["$lte"] = end_date
                except:
                    pass
            if date_filter:
                query["created_at"] = date_filter

        # Domain filter
        if domain_id:
            try:
                query["domain_id"] = ObjectId(domain_id)
            except:
                pass

        # Super admin can filter by a specific admin
        filter_admin_id_str = request.args.get("admin_id")
        if claims.get("role") == "super_admin" and filter_admin_id_str:
            try:
                filter_admin_id = ObjectId(filter_admin_id_str)
                filter_domains = list(db.domains.find({"admin_id": filter_admin_id}))
                filter_domain_ids = [d["_id"] for d in filter_domains]
                if "domain_id" in query:
                    if query["domain_id"] not in filter_domain_ids:
                        query["domain_id"] = {"$in": []}
                else:
                    query["domain_id"] = {"$in": filter_domain_ids}
            except Exception:
                pass

        # Admin visibility: regular admin sees only own domains
        elif claims.get("role") != "super_admin":
            admin_domains = list(db.domains.find({"admin_id": admin_id}))
            domain_ids = [d["_id"] for d in admin_domains]

            if "domain_id" in query:
                if query["domain_id"] not in domain_ids:
                    return jsonify({"error": "You can only view your own domain reports"}), 403
            else:
                query["domain_id"] = {"$in": domain_ids}

        # Fetch subscriptions
        subscriptions = list(
            db.subscriptions.find(query)
            .sort("created_at", -1)
        )

        # Get domain info for each subscription
        for sub in subscriptions:
            domain = db.domains.find_one({"_id": sub["domain_id"]})
            sub["domain_full_key"] = domain.get("full_key", "") if domain else ""

            # Convert ObjectId to string for JSON
            sub["_id"] = str(sub["_id"])
            sub["domain_id"] = str(sub["domain_id"])
            sub["admin_id"] = str(sub["admin_id"])
            sub["created_at"] = sub["created_at"].isoformat() if sub.get("created_at") else ""
            sub["start_date"] = sub["start_date"].isoformat() if sub.get("start_date") else ""
            sub["end_date"] = sub["end_date"].isoformat() if sub.get("end_date") else ""

        # Calculate totals
        total_amount = sum(sub.get("price") or 0 for sub in subscriptions)
        total_count = len(subscriptions)

        # Get available domains for dropdown (for filtering)
        if claims.get("role") == "super_admin":
            available_domains = list(db.domains.find({}, {"_id": 1, "full_key": 1}))
        else:
            available_domains = list(
                db.domains.find({"admin_id": admin_id}, {"_id": 1, "full_key": 1})
            )

        for domain in available_domains:
            domain["_id"] = str(domain["_id"])

        return jsonify({
            "subscriptions": subscriptions,
            "total_count": total_count,
            "total_amount": total_amount,
            "available_domains": available_domains
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@subscriptions_bp.route("/monthly-report", methods=["GET"])
@jwt_required()
def get_monthly_report():
    """Get monthly subscription report with domain, user, and admin details."""
    try:
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        # Get month and year from query params (format: YYYY-MM)
        month_str = request.args.get("month", "")  # e.g., "2026-06"

        if not month_str:
            return jsonify({"error": "Month parameter required (format: YYYY-MM)"}), 400

        try:
            year, month = month_str.split('-')
            year, month = int(year), int(month)
            # Create start and end dates for the month
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            # Get first day of next month
            if month == 12:
                end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        except:
            return jsonify({"error": "Invalid month format. Use YYYY-MM"}), 400

        # Build query for the month
        query = {
            "created_at": {
                "$gte": start_date,
                "$lt": end_date
            }
        }

        # Super admin can filter by specific admin
        filter_admin_id_str = request.args.get("admin_id")
        if claims.get("role") == "super_admin" and filter_admin_id_str:
            try:
                filter_admin_id = ObjectId(filter_admin_id_str)
                filter_domains = list(db.domains.find({"admin_id": filter_admin_id}))
                query["domain_id"] = {"$in": [d["_id"] for d in filter_domains]}
            except Exception:
                pass
        elif claims.get("role") != "super_admin":
            admin_domains = list(db.domains.find({"admin_id": admin_id}))
            domain_ids = [d["_id"] for d in admin_domains]
            query["domain_id"] = {"$in": domain_ids}

        # Get all subscriptions for the month
        subscriptions = list(db.subscriptions.find(query))

        # Build detailed report with domain and user info
        report_data = []
        domain_stats = {}

        for sub in subscriptions:
            domain = db.domains.find_one({"_id": sub["domain_id"]})
            user = db.users.find_one({"_id": domain["user_id"]}) if domain else None
            admin = db.admins.find_one({"_id": sub["admin_id"]})

            domain_name = domain.get("full_key", "") if domain else ""
            user_name = user.get("name", "—") if user else "—"
            admin_name = admin.get("username", "—") if admin else "—"

            # Use domain_full_key as grouping key
            key = domain_name

            if key not in domain_stats:
                domain_stats[key] = {
                    "domain": domain_name,
                    "domain_id": str(domain["_id"]) if domain else "",
                    "user_name": user_name,
                    "user_id": str(user["_id"]) if user else "",
                    "admin_name": admin_name,
                    "admin_id": str(admin["_id"]) if admin else "",
                    "subscriptions": [],
                    "count": 0,
                    "total_amount": 0
                }

            domain_stats[key]["subscriptions"].append({
                "id": str(sub["_id"]),
                "type": sub.get("subscription_type", ""),
                "price": sub.get("price"),
                "date": sub.get("created_at").isoformat() if sub.get("created_at") else ""
            })
            domain_stats[key]["count"] += 1
            domain_stats[key]["total_amount"] += sub.get("price") or 0

        # Convert to list
        report_data = list(domain_stats.values())

        # Calculate totals
        total_count = sum(item["count"] for item in report_data)
        total_amount = sum(item["total_amount"] for item in report_data)

        return jsonify({
            "month": month_str,
            "report_data": report_data,
            "total_records": total_count,
            "total_amount": total_amount,
            "count": len(report_data)  # number of unique domains
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
