import logging
from email.mime.image import MIMEImage
from html import escape
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGO_PATH = PROJECT_ROOT / "frontend" / "src" / "assets" / "WhatsA mail.jpeg"


def _from_email():
    configured = settings.DEFAULT_FROM_EMAIL
    if "<" in configured:
        return configured
    return f"Luxmor TalentForge <{configured}>"


def _email_html(*, preheader, eyebrow, heading, greeting, paragraphs, details, closing):
    detail_rows = "".join(
        f"""
        <tr>
          <td style="padding:8px 0;color:#747386;font-size:13px;width:42%;">{escape(label)}</td>
          <td style="padding:8px 0;color:#17152b;font-size:13px;font-weight:700;">{escape(str(value))}</td>
        </tr>
        """
        for label, value in details
    )
    body_paragraphs = "".join(
        f'<p style="margin:0 0 15px;color:#5f5c6e;font-size:15px;line-height:1.7;">{escape(text)}</p>'
        for text in paragraphs
    )
    return f"""<!doctype html>
<html lang="en">
  <body style="margin:0;background:#f5f4f9;font-family:Arial,sans-serif;color:#17152b;">
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;">{escape(preheader)}</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f4f9;padding:32px 12px;">
      <tr><td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:620px;background:#fff;border:1px solid #e8e5f0;border-radius:18px;overflow:hidden;">
          <tr>
            <td style="padding:24px 34px;background:#fff;border-bottom:1px solid #eeeaf5;">
              <img src="cid:luxmor-logo" width="250" alt="Luxmor AI Technologies" style="display:block;width:250px;max-width:80%;height:auto;">
            </td>
          </tr>
          <tr>
            <td style="padding:36px 34px 12px;background:linear-gradient(135deg,#19162f,#30245c);">
              <div style="color:#aa98ff;font-size:11px;font-weight:700;letter-spacing:1.8px;text-transform:uppercase;">{escape(eyebrow)}</div>
              <h1 style="margin:12px 0 10px;color:#fff;font-size:30px;line-height:1.25;">{escape(heading)}</h1>
              <p style="margin:0;color:#c8c2d8;font-size:15px;line-height:1.6;">Luxmor TalentForge · Campus Recruitment</p>
            </td>
          </tr>
          <tr>
            <td style="padding:30px 34px 12px;">
              <p style="margin:0 0 18px;color:#17152b;font-size:16px;font-weight:700;">{escape(greeting)}</p>
              {body_paragraphs}
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:22px 0;padding:14px 20px;background:#f7f5ff;border:1px solid #e8e3ff;border-radius:12px;">
                {detail_rows}
              </table>
              <p style="margin:22px 0 8px;color:#5f5c6e;font-size:14px;line-height:1.7;">{escape(closing)}</p>
              <p style="margin:0;color:#17152b;font-size:14px;font-weight:700;">Luxmor Recruitment Team</p>
            </td>
          </tr>
          <tr>
            <td style="padding:22px 34px;background:#faf9fc;border-top:1px solid #eeeaf5;color:#8a8797;font-size:11px;line-height:1.6;">
              This is an automated transactional message about your Luxmor TalentForge application. Please do not share assessment access or candidate information.
            </td>
          </tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""


def _send(*, candidate, subject, plain_text, html):
    if not settings.EMAIL_NOTIFICATIONS_ENABLED:
        logger.info("Candidate email skipped because SMTP is not configured.")
        return False
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=_from_email(),
            to=[candidate.email],
        )
        message.attach_alternative(html, "text/html")
        if LOGO_PATH.exists():
            logo = MIMEImage(LOGO_PATH.read_bytes(), _subtype="jpeg")
            logo.add_header("Content-ID", "<luxmor-logo>")
            logo.add_header(
                "Content-Disposition", "inline", filename="luxmor-logo.jpeg"
            )
            message.attach(logo)
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception(
            "Could not send candidate email.",
            extra={"candidate_id": str(candidate.id), "email_type": subject},
        )
        return False


def send_registration_email(candidate):
    application_id = str(candidate.id)[:8].upper()
    role = candidate.get_role_display()
    location = candidate.get_preferred_location_display()
    paragraphs = [
        "Your candidate profile has been registered successfully.",
        "Your assessment includes aptitude, role-specific technical questions, and practical coding challenges. Please return to the browser used for registration when you are ready to continue.",
    ]
    details = [
        ("Application ID", application_id),
        ("Job profile", role),
        ("Preferred location", location),
        ("Assessment stages", "Aptitude · Role skills · Coding"),
    ]
    plain = (
        f"Hi {candidate.name},\n\nYour Luxmor TalentForge application was registered successfully.\n"
        f"Application ID: {application_id}\nJob profile: {role}\nPreferred location: {location}\n\n"
        "Complete all three assessment stages in the browser used for registration.\n\n"
        "Luxmor Recruitment Team"
    )
    html = _email_html(
        preheader="Your Luxmor TalentForge candidate profile is ready.",
        eyebrow="Registration confirmed",
        heading="Your application is ready",
        greeting=f"Hi {candidate.name},",
        paragraphs=paragraphs,
        details=details,
        closing="We wish you the very best for your assessment.",
    )
    return _send(
        candidate=candidate,
        subject="Luxmor TalentForge — Registration confirmed",
        plain_text=plain,
        html=html,
    )


def send_completion_email(candidate):
    application_id = str(candidate.id)[:8].upper()
    role = candidate.get_role_display()
    paragraphs = [
        "Your complete Luxmor TalentForge assessment has been submitted successfully.",
        "The Luxmor recruitment team will review your responses, coding evaluation, and assessment integrity record. Shortlisted candidates will be contacted using the details provided during registration.",
    ]
    details = [
        ("Application ID", application_id),
        ("Job profile", role),
        ("Assessment status", "Successfully submitted"),
        ("Next step", "Recruitment team review"),
    ]
    plain = (
        f"Hi {candidate.name},\n\nYour complete Luxmor TalentForge assessment was submitted successfully.\n"
        f"Application ID: {application_id}\nJob profile: {role}\n\n"
        "The recruitment team will contact shortlisted candidates. Assessment results remain confidential.\n\n"
        "Luxmor Recruitment Team"
    )
    html = _email_html(
        preheader="Your Luxmor TalentForge assessment has been submitted.",
        eyebrow="Assessment completed",
        heading="Submission received successfully",
        greeting=f"Well done, {candidate.name}.",
        paragraphs=paragraphs,
        details=details,
        closing="Assessment results are confidential and will not be displayed in the candidate portal.",
    )
    return _send(
        candidate=candidate,
        subject="Luxmor TalentForge — Assessment submitted",
        plain_text=plain,
        html=html,
    )
