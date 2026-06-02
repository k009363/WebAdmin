import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_TIMEOUT = 10  # seconds — fail fast instead of hanging


def send_email(smtp_cfg: dict, to: str, subject: str, html_body: str, text_body: str = ""):
    """
    Send an email using SMTP credentials from DB settings.
    Supports STARTTLS (port 587) and SSL (port 465) automatically.
    smtp_cfg keys: host, port, username, password, from_name, from_email, use_tls
    Raises exception with a clear message on failure.
    """
    host     = (smtp_cfg.get("host") or "").strip()
    port     = int(smtp_cfg.get("port") or 587)
    username = (smtp_cfg.get("username") or "").strip()
    password = (smtp_cfg.get("password") or "").strip()
    use_tls  = smtp_cfg.get("use_tls", True)
    from_email = (smtp_cfg.get("from_email") or "").strip()
    from_name  = (smtp_cfg.get("from_name") or "Website").strip()

    if not host:
        raise ValueError("SMTP host is not configured")
    if not from_email:
        raise ValueError("From email is not configured")
    if not to:
        raise ValueError("Recipient email is missing")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{from_email}>"
    msg["To"]      = to

    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        # Port 465 → SSL directly; 587/25 → STARTTLS
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, timeout=SMTP_TIMEOUT, context=context) as server:
                server.ehlo()
                if username and password:
                    server.login(username, password)
                server.sendmail(from_email, to, msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                if username and password:
                    server.login(username, password)
                server.sendmail(from_email, to, msg.as_string())

    except smtplib.SMTPAuthenticationError:
        raise Exception(f"SMTP authentication failed — check username/password for {host}")
    except smtplib.SMTPConnectError as e:
        raise Exception(f"Cannot connect to SMTP server {host}:{port} — {e}")
    except smtplib.SMTPRecipientsRefused:
        raise Exception(f"Recipient address refused: {to}")
    except smtplib.SMTPSenderRefused:
        raise Exception(f"Sender address refused: {from_email}")
    except TimeoutError:
        raise Exception(f"Connection to {host}:{port} timed out after {SMTP_TIMEOUT}s — check host/port")
    except ConnectionRefusedError:
        raise Exception(f"Connection refused by {host}:{port} — server may be down or port blocked")
    except ssl.SSLError as e:
        raise Exception(f"SSL error connecting to {host}:{port} — try port 587 with TLS instead. Detail: {e}")
    except OSError as e:
        raise Exception(f"Network error connecting to {host}:{port} — {e}")


def build_contact_email(contact: dict, site_name: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
      <h2 style="color:#4f46e5;margin-bottom:4px;">New Contact Form Submission</h2>
      <p style="color:#6b7280;margin-bottom:24px;">From <strong>{site_name}</strong></p>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;width:30%;">Name</td><td style="padding:10px;">{contact.get('name','')}</td></tr>
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;">Email</td><td style="padding:10px;"><a href="mailto:{contact.get('email','')}">{contact.get('email','')}</a></td></tr>
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;">Phone</td><td style="padding:10px;">{contact.get('phone','—')}</td></tr>
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;">Subject</td><td style="padding:10px;">{contact.get('subject','')}</td></tr>
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;vertical-align:top;">Message</td><td style="padding:10px;">{contact.get('message','').replace(chr(10),'<br>')}</td></tr>
      </table>
      <p style="color:#9ca3af;font-size:12px;margin-top:24px;">Sent via Dynamic Websites Platform</p>
    </div>
    """


def build_feedback_email(feedback: dict, site_name: str) -> str:
    stars = '★' * int(feedback.get('rating') or 0) + '☆' * (5 - int(feedback.get('rating') or 0))
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
      <h2 style="color:#4f46e5;margin-bottom:4px;">New Feedback Submission</h2>
      <p style="color:#6b7280;margin-bottom:24px;">From <strong>{site_name}</strong></p>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;width:30%;">Name</td><td style="padding:10px;">{feedback.get('name','')}</td></tr>
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;">Email</td><td style="padding:10px;"><a href="mailto:{feedback.get('email','')}">{feedback.get('email','')}</a></td></tr>
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;">Rating</td><td style="padding:10px;">{stars} ({feedback.get('rating','')} / 5)</td></tr>
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;">Category</td><td style="padding:10px;">{feedback.get('category','—')}</td></tr>
        <tr><td style="padding:10px;background:#f8fafc;font-weight:600;vertical-align:top;">Feedback</td><td style="padding:10px;">{feedback.get('feedback','').replace(chr(10),'<br>')}</td></tr>
      </table>
      <p style="color:#9ca3af;font-size:12px;margin-top:24px;">Sent via Dynamic Websites Platform</p>
    </div>
    """


def build_auto_reply_email(contact: dict, site_name: str) -> str:
    first_name = (contact.get('name') or 'there').split()[0]
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px;">
      <h2 style="color:#4f46e5;">Thank you, {first_name}!</h2>
      <p>We have received your message and will get back to you within 24 hours.</p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;">
      <p style="color:#6b7280;font-size:13px;"><strong>Your message:</strong><br>{contact.get('message','').replace(chr(10),'<br>')}</p>
      <p style="color:#9ca3af;font-size:12px;margin-top:24px;">— The {site_name} Team</p>
    </div>
    """
