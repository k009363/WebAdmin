"""
Script to update existing admin record with role and page permissions.
Run this if your existing admin doesn't have the 'role' field.
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "dynamic_websites")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(f"\n📦 Connecting to MongoDB: {DB_NAME}")

# All available pages in admin panel
ALL_PAGES = [
    "dashboard",
    "domains",
    "users",
    "templates",
    "blog",
    "contacts",
    "feedback",
    "settings",
    "reports",
    "websitePreview",
    "adminManagement",
    "adminContact"
]

# Check existing admin
admin = db.admins.find_one({"username": "admin"})

if not admin:
    print("❌ Admin not found!")
    exit(1)

print(f"✅ Found admin: {admin['username']}")
print(f"   Current fields: {list(admin.keys())}")

# Check if role field exists
if "role" in admin and admin["role"] == "super_admin":
    print(f"✅ Admin already has role='super_admin'")
    print(f"✅ No update needed!")
    exit(0)

print("\n🔄 Updating admin with role and page_permissions...")

# Update the admin document
update_result = db.admins.update_one(
    {"username": "admin"},
    {
        "$set": {
            "role": "super_admin",
            "email": "admin@yourdomain.com",
            "phone": "+1 (555) 000-0000",
            "page_permissions": ALL_PAGES,
            "updated_at": datetime.now(timezone.utc)
        }
    }
)

if update_result.modified_count > 0:
    print("✅ Admin updated successfully!")

    # Show updated document
    updated_admin = db.admins.find_one({"username": "admin"})
    print("\n📋 Updated Admin Document:")
    print(f"   Username: {updated_admin.get('username')}")
    print(f"   Role: {updated_admin.get('role')}")
    print(f"   Email: {updated_admin.get('email')}")
    print(f"   Phone: {updated_admin.get('phone')}")
    print(f"   Page Permissions: {len(updated_admin.get('page_permissions', []))} pages")
    print(f"      {', '.join(updated_admin.get('page_permissions', []))}")
    print("\n✅ Database update complete!")
else:
    print("⚠️ No changes made")

client.close()
