import cloudinary
import cloudinary.uploader
import os


def init_cloudinary(cloud_name=None, api_key=None, api_secret=None):
    cloudinary.config(
        cloud_name=cloud_name or os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=api_key or os.getenv("CLOUDINARY_API_KEY"),
        api_secret=api_secret or os.getenv("CLOUDINARY_API_SECRET"),
    )


def upload_image(file_stream, folder="dynamic_websites", public_id=None):
    """Upload a file stream to Cloudinary and return the secure URL."""
    init_cloudinary()
    opts = {"folder": folder, "resource_type": "image"}
    if public_id:
        opts["public_id"] = public_id
    result = cloudinary.uploader.upload(file_stream, **opts)
    return result.get("secure_url")


def upload_from_settings(file_stream, folder="dynamic_websites", settings=None):
    """Upload using Cloudinary credentials stored in DB settings."""
    if settings:
        c = settings.get("cloudinary", {})
        init_cloudinary(c.get("cloud_name"), c.get("api_key"), c.get("api_secret"))
    return upload_image(file_stream, folder)
