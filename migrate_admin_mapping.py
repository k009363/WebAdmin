"""
Migration: Fix admin_id mapping for users and domains.
- Users without admin_id → assign to super admin
- Domains without admin_id or with super_admin's admin_id but having a user →
  derive admin_id from the linked user's admin_id
Run: python3 migrate_admin_mapping.py
"""
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("MONGO_DB",  "dynamic_websites")

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

# Find super admin
super_admin = db.admins.find_one({"role": "super_admin"})
if not super_admin:
    print("ERROR: No super_admin found in DB")
    exit(1)

super_admin_id = super_admin["_id"]
print(f"\nSuper Admin: {super_admin['username']} ({super_admin_id})\n")

# ── Step 1: Fix users without admin_id ──────────────────────────────────────
print("=" * 55)
print("STEP 1: Users without admin_id")
print("=" * 55)

users_no_admin = list(db.users.find({"admin_id": {"$exists": False}}))
print(f"Found {len(users_no_admin)} users without admin_id → assigning to super admin\n")

for user in users_no_admin:
    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"admin_id": super_admin_id}}
    )
    print(f"  [FIXED] User: {user.get('name','?')} ({user.get('email','?')}) → admin_id = super_admin")

# ── Step 2: Fix domains — derive admin_id from linked user ──────────────────
print(f"\n{'=' * 55}")
print("STEP 2: Domains — check and fix admin_id mapping")
print("=" * 55)

all_domains = list(db.domains.find({}))
print(f"Found {len(all_domains)} total domains\n")

domain_updated = 0
domain_skipped = 0

for domain in all_domains:
    current_admin_id = domain.get("admin_id")
    user_id = domain.get("user_id")

    # If domain has a linked user, derive admin_id from user
    if user_id:
        user = db.users.find_one({"_id": user_id})
        if user and user.get("admin_id"):
            correct_admin_id = user["admin_id"]
            if current_admin_id != correct_admin_id:
                db.domains.update_one(
                    {"_id": domain["_id"]},
                    {"$set": {"admin_id": correct_admin_id}}
                )
                # Get admin username for display
                admin = db.admins.find_one({"_id": correct_admin_id})
                admin_name = admin["username"] if admin else str(correct_admin_id)
                print(f"  [UPDATED] {domain['full_key']:<35} → admin = {admin_name}")
                domain_updated += 1
            else:
                domain_skipped += 1
        else:
            domain_skipped += 1
    else:
        domain_skipped += 1

print(f"\n  Updated : {domain_updated} domains")
print(f"  Skipped : {domain_skipped} domains (no change needed / no linked user)")

# ── Step 3: Summary ─────────────────────────────────────────────────────────
print(f"\n{'=' * 55}")
print("FINAL MAPPING SUMMARY")
print("=" * 55)

admins = list(db.admins.find({}))
for admin in admins:
    admin_id = admin["_id"]
    domain_count = db.domains.count_documents({"admin_id": admin_id})
    user_count   = db.users.count_documents({"admin_id": admin_id})
    role = admin.get("role", "admin")
    print(f"\n  [{role.upper()}] {admin['username']}")
    print(f"    Domains : {domain_count}")
    print(f"    Users   : {user_count}")

print()
