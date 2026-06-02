"""
Migration: Add subscription field to existing domains that don't have it.
- Domains without subscription  → type: "none", start_date: created_at, end_date: created_at + 30 days
- Domains with incomplete subscription fields → fill in missing fields
Run: python3 migrate_subscriptions.py
"""
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("MONGO_DB",  "dynamic_websites")

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

now = datetime.now(timezone.utc)

domains = list(db.domains.find({}))
print(f"\nFound {len(domains)} total domains\n")

updated = 0
skipped = 0

for domain in domains:
    sub = domain.get("subscription")
    needs_update = False
    update_fields = {}

    if not sub:
        # No subscription at all — add 30-day trial from creation date
        created_at = domain.get("created_at", now)
        if not isinstance(created_at, datetime):
            created_at = now

        update_fields["subscription"] = {
            "type": "none",
            "start_date": created_at,
            "end_date": created_at + timedelta(days=30),
            "price": None,
            "is_active": True
        }
        needs_update = True
        print(f"  [ADD]    {domain['full_key']} → trial from {created_at.strftime('%d %b %Y')} to {(created_at + timedelta(days=30)).strftime('%d %b %Y')}")

    else:
        # Has subscription — fill in any missing fields
        patch = {}

        if not sub.get("type"):
            patch["subscription.type"] = "none"

        if not sub.get("start_date"):
            created_at = domain.get("created_at", now)
            patch["subscription.start_date"] = created_at if isinstance(created_at, datetime) else now

        if not sub.get("end_date"):
            start = sub.get("start_date") or domain.get("created_at") or now
            if not isinstance(start, datetime):
                start = now
            patch["subscription.end_date"] = start + timedelta(days=30)

        if "is_active" not in sub:
            patch["subscription.is_active"] = True

        if patch:
            update_fields.update(patch)
            needs_update = True
            print(f"  [PATCH]  {domain['full_key']} → filling missing fields: {list(patch.keys())}")
        else:
            skipped += 1

    if needs_update:
        db.domains.update_one(
            {"_id": domain["_id"]},
            {"$set": update_fields}
        )
        updated += 1

print(f"\n{'='*50}")
print(f"  Updated : {updated} domains")
print(f"  Skipped : {skipped} domains (already complete)")
print(f"{'='*50}\n")

# Summary of all domains after migration
print("Current subscription status after migration:\n")
for domain in db.domains.find({}, {"full_key": 1, "subscription": 1}):
    sub = domain.get("subscription", {})
    end_date = sub.get("end_date")
    if end_date and isinstance(end_date, datetime):
        end_date_aware = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
        days_left = (end_date_aware - now).days
        status = f"EXPIRED ({abs(days_left)}d ago)" if days_left < 0 else f"{days_left}d remaining"
    else:
        status = "no end_date"
    sub_type = sub.get("type", "—")
    print(f"  {domain['full_key']:<35} type={sub_type:<10} {status}")

print()
