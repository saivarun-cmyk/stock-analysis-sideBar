"""
services/notification_service.py

Purpose
-------
Defines the notification interface ahead of need. Today it only logs;
later, Telegram/WhatsApp backends can be dropped in here without touching
app.py or any other layer.

Inputs
------
message: str
channel: str  - "log" (default) | "telegram" | "whatsapp" (not yet implemented)

Outputs
-------
bool - True if the notification was "sent" (logged) successfully.

How it connects
----------------
app.py calls send_notification() from the placeholder "Telegram Alerts"
section. Swap the body of the "telegram"/"whatsapp" branches for real API
calls when ready — no other file needs to change.
"""

from utils.helpers import get_logger

logger = get_logger(__name__)


def send_notification(message: str, channel: str = "log") -> bool:
    """
    Stub notification dispatcher.

    channel="log"      -> writes to the application log (always available)
    channel="telegram"  -> TODO: implement via Telegram Bot API
    channel="whatsapp"  -> TODO: implement via WhatsApp Business API
    """
    if channel == "log":
        logger.info("[NOTIFICATION] %s", message)
        return True

    if channel == "telegram":
        logger.warning("Telegram channel not yet implemented. Message dropped: %s", message)
        return False

    if channel == "whatsapp":
        logger.warning("WhatsApp channel not yet implemented. Message dropped: %s", message)
        return False

    logger.error("Unknown notification channel: %s", channel)
    return False
