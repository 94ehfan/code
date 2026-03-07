import logging

from app.config import settings
from app.models import Draft, NotificationPreference, User

logger = logging.getLogger(__name__)


def send_sms(to: str, body: str):
    """Send an SMS via Twilio."""
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.warning("Twilio not configured — skipping SMS to %s: %s", to, body)
        return

    try:
        from twilio.rest import Client

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        client.messages.create(
            body=body,
            from_=settings.twilio_phone_number,
            to=to,
        )
        logger.info("SMS sent to %s", to)
    except Exception:
        logger.exception("Failed to send SMS to %s", to)


def notify_turn(user: User, draft: Draft):
    """Notify a user that it's their turn to pick."""
    if user.notification_preference == NotificationPreference.NONE:
        return
    if not user.phone_number:
        logger.warning("User %s has no phone number for SMS", user.username)
        return

    body = (
        f"Hey {user.display_name}! It's your turn to pick in "
        f"'{draft.name}' (Round {draft.current_round}). "
        f"Pick now: {settings.app_url}/draft/{draft.id}"
    )
    send_sms(user.phone_number, body)


def notify_draft_started(draft: Draft, participants: list):
    """Notify all participants that the draft has started."""
    for participant in participants:
        user = participant.user
        if user.notification_preference == NotificationPreference.NONE:
            continue
        if not user.phone_number:
            continue

        body = (
            f"The '{draft.name}' ticket draft has started! "
            f"Follow along: {settings.app_url}/draft/{draft.id}"
        )
        send_sms(user.phone_number, body)
