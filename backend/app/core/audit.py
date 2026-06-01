import logging
from datetime import datetime
from typing import Optional

audit_logger = logging.getLogger("audit")


def log_event(event: str, user_id: Optional[str] = None, ip: Optional[str] = None, **details):
    audit_logger.info({
        "event": event,
        "user_id": user_id,
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat(),
        **details,
    })
