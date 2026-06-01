from __future__ import annotations

import json
import smtplib
from dataclasses import dataclass, field
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

import requests


class NotificationType(str, Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


@dataclass
class Notification:
    id: str
    notification_type: NotificationType
    recipient: str
    subject: str
    body: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None


@dataclass
class Subscription:
    skill_id: str
    user_id: str
    notification_types: List[NotificationType] = field(default_factory=lambda: [NotificationType.IN_APP])
    created_at: datetime = field(default_factory=datetime.utcnow)


class NotificationService:

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        smtp_from: Optional[str] = None,
        webhook_registry: Optional[Dict[str, str]] = None,
        in_app_handler: Optional[Callable] = None,
    ):
        self.smtp_host = smtp_host or "localhost"
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_from = smtp_from or "noreply@skill-library.dev"
        self.webhook_registry: Dict[str, str] = webhook_registry or {}
        self.in_app_handler = in_app_handler

        self._subscriptions: Dict[str, Set[str]] = {}
        self._notifications: List[Notification] = []
        self._user_email_map: Dict[str, str] = {}
        self._user_webhook_map: Dict[str, str] = {}
        self._skills_db: Dict[str, Dict[str, Any]] = {}

    def set_skills_db(self, skills: Dict[str, Dict[str, Any]]) -> None:
        self._skills_db = skills

    def set_user_email_map(self, user_emails: Dict[str, str]) -> None:
        self._user_email_map = user_emails

    def set_user_webhook_map(self, user_webhooks: Dict[str, str]) -> None:
        self._user_webhook_map = user_webhooks

    def send_skill_update_notification(
        self,
        skill_id: str,
        change_type: str,
        changed_by: Optional[str] = None,
    ) -> List[Notification]:
        subscribers = self.get_subscribers(skill_id)
        skill = self._skills_db.get(skill_id, {})
        skill_name = skill.get("name", skill_id)

        change_descriptions = {
            "updated": "has been updated",
            "deprecated": "has been deprecated",
            "version_bump": "has a new version",
            "breaking_change": "has breaking changes",
            "deleted": "has been removed",
        }
        change_text = change_descriptions.get(change_type, f"has changed ({change_type})")

        subject = f"Skill Update: {skill_name} {change_text}"
        body = self._build_update_notification_body(
            skill_name=skill_name,
            skill_id=skill_id,
            change_type=change_type,
            changed_by=changed_by,
        )

        notifications: List[Notification] = []

        for user_id in subscribers:
            user_notifications = self._send_to_user(
                user_id=user_id,
                subject=subject,
                body=body,
                metadata={
                    "skill_id": skill_id,
                    "change_type": change_type,
                    "changed_by": changed_by,
                },
            )
            notifications.extend(user_notifications)

        return notifications

    def notify_new_skill(self, skill_id: str, author_id: Optional[str] = None) -> List[Notification]:
        skill = self._skills_db.get(skill_id, {})
        skill_name = skill.get("name", skill_id)
        category = skill.get("category", "other")

        subject = f"New Skill Published: {skill_name}"
        body = self._build_new_skill_notification_body(
            skill_name=skill_name,
            skill_id=skill_id,
            category=category,
            author_id=author_id,
        )

        subscribers = self.get_subscribers(skill_id)
        if author_id:
            subscribers.add(author_id)

        notifications: List[Notification] = []

        for user_id in subscribers:
            user_notifications = self._send_to_user(
                user_id=user_id,
                subject=subject,
                body=body,
                metadata={
                    "skill_id": skill_id,
                    "event": "new_skill",
                    "author_id": author_id,
                },
            )
            notifications.extend(user_notifications)

        return notifications

    def notify_skill_reviewed(
        self, skill_id: str, rating: float, reviewer_id: Optional[str] = None
    ) -> List[Notification]:
        skill = self._skills_db.get(skill_id, {})
        skill_name = skill.get("name", skill_id)
        author_id = skill.get("author_id")

        subject = f"New Review for {skill_name}: {rating}/5.0"
        body = self._build_review_notification_body(
            skill_name=skill_name,
            skill_id=skill_id,
            rating=rating,
            reviewer_id=reviewer_id,
        )

        notifications: List[Notification] = []

        if author_id:
            user_notifications = self._send_to_user(
                user_id=author_id,
                subject=subject,
                body=body,
                metadata={
                    "skill_id": skill_id,
                    "event": "review",
                    "rating": rating,
                    "reviewer_id": reviewer_id,
                },
            )
            notifications.extend(user_notifications)

        subscribers = self.get_subscribers(skill_id)
        if author_id:
            subscribers.discard(author_id)

        for user_id in subscribers:
            user_notifications = self._send_to_user(
                user_id=user_id,
                subject=subject,
                body=body,
                metadata={
                    "skill_id": skill_id,
                    "event": "review",
                    "rating": rating,
                },
            )
            notifications.extend(user_notifications)

        return notifications

    def subscribe_to_skill(
        self,
        skill_id: str,
        user_id: str,
        notification_types: Optional[List[NotificationType]] = None,
    ) -> Subscription:
        if skill_id not in self._subscriptions:
            self._subscriptions[skill_id] = set()

        self._subscriptions[skill_id].add(user_id)

        subscription = Subscription(
            skill_id=skill_id,
            user_id=user_id,
            notification_types=notification_types or [NotificationType.IN_APP],
        )
        return subscription

    def unsubscribe_from_skill(self, skill_id: str, user_id: str) -> bool:
        if skill_id in self._subscriptions:
            self._subscriptions[skill_id].discard(user_id)
            if not self._subscriptions[skill_id]:
                del self._subscriptions[skill_id]
            return True
        return False

    def get_subscribers(self, skill_id: str) -> Set[str]:
        return self._subscriptions.get(skill_id, set()).copy()

    def _send_to_user(
        self,
        user_id: str,
        subject: str,
        body: str,
        metadata: Dict[str, Any],
    ) -> List[Notification]:
        notifications: List[Notification] = []

        email = self._user_email_map.get(user_id)
        if email:
            notification = self._send_email_notification(
                recipient=email,
                subject=subject,
                body=body,
                metadata=metadata,
            )
            notifications.append(notification)

        webhook_url = self._user_webhook_map.get(user_id)
        if webhook_url:
            notification = self._send_webhook_notification(
                webhook_url=webhook_url,
                subject=subject,
                body=body,
                metadata=metadata,
            )
            notifications.append(notification)

        in_app_notification = self._send_in_app_notification(
            user_id=user_id,
            subject=subject,
            body=body,
            metadata=metadata,
        )
        notifications.append(in_app_notification)

        return notifications

    def _send_email_notification(
        self,
        recipient: str,
        subject: str,
        body: str,
        metadata: Dict[str, Any],
    ) -> Notification:
        import uuid

        notification = Notification(
            id=str(uuid.uuid4()),
            notification_type=NotificationType.EMAIL,
            recipient=recipient,
            subject=subject,
            body=body,
            metadata=metadata,
        )

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.smtp_from
            msg["To"] = recipient
            msg["Subject"] = subject

            html_body = self._render_html_body(body)

            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            notification.status = "sent"
            notification.sent_at = datetime.utcnow()
        except Exception as e:
            notification.status = "failed"
            notification.metadata["error"] = str(e)

        self._notifications.append(notification)
        return notification

    def _send_webhook_notification(
        self,
        webhook_url: str,
        subject: str,
        body: str,
        metadata: Dict[str, Any],
    ) -> Notification:
        import uuid

        notification = Notification(
            id=str(uuid.uuid4()),
            notification_type=NotificationType.WEBHOOK,
            recipient=webhook_url,
            subject=subject,
            body=body,
            metadata=metadata,
        )

        try:
            payload = {
                "subject": subject,
                "body": body,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat(),
            }

            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()

            notification.status = "sent"
            notification.sent_at = datetime.utcnow()
        except Exception as e:
            notification.status = "failed"
            notification.metadata["error"] = str(e)

        self._notifications.append(notification)
        return notification

    def _send_in_app_notification(
        self,
        user_id: str,
        subject: str,
        body: str,
        metadata: Dict[str, Any],
    ) -> Notification:
        import uuid

        notification = Notification(
            id=str(uuid.uuid4()),
            notification_type=NotificationType.IN_APP,
            recipient=user_id,
            subject=subject,
            body=body,
            metadata=metadata,
        )

        if self.in_app_handler:
            try:
                self.in_app_handler(
                    user_id=user_id,
                    subject=subject,
                    body=body,
                    metadata=metadata,
                )
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
            except Exception as e:
                notification.status = "failed"
                notification.metadata["error"] = str(e)
        else:
            notification.status = "stored"
            notification.metadata["note"] = "No in-app handler configured"

        self._notifications.append(notification)
        return notification

    def _build_update_notification_body(
        self,
        skill_name: str,
        skill_id: str,
        change_type: str,
        changed_by: Optional[str] = None,
    ) -> str:
        lines = [
            f"Skill '{skill_name}' ({skill_id}) has been updated.",
            f"",
            f"Change type: {change_type}",
        ]
        if changed_by:
            lines.append(f"Changed by: {changed_by}")
        lines.extend([
            "",
            "You are receiving this notification because you are subscribed to this skill.",
            "Manage your notification preferences in your account settings.",
        ])
        return "\n".join(lines)

    def _build_new_skill_notification_body(
        self,
        skill_name: str,
        skill_id: str,
        category: str,
        author_id: Optional[str] = None,
    ) -> str:
        lines = [
            f"A new skill has been published: '{skill_name}'",
            f"",
            f"Category: {category}",
        ]
        if author_id:
            lines.append(f"Author: {author_id}")
        lines.extend([
            f"",
            f"View the skill: /skills/{skill_id}",
            "",
            "You are receiving this notification because you are subscribed to this skill's category.",
            "Manage your notification preferences in your account settings.",
        ])
        return "\n".join(lines)

    def _build_review_notification_body(
        self,
        skill_name: str,
        skill_id: str,
        rating: float,
        reviewer_id: Optional[str] = None,
    ) -> str:
        lines = [
            f"Skill '{skill_name}' has received a new review.",
            f"",
            f"Rating: {rating}/5.0",
        ]
        if reviewer_id:
            lines.append(f"Reviewer: {reviewer_id}")
        lines.extend([
            f"",
            f"View the skill: /skills/{skill_id}",
            "",
            "Manage your notification preferences in your account settings.",
        ])
        return "\n".join(lines)

    def _render_html_body(self, text_body: str) -> str:
        html_lines = ["<html><body>"]
        for line in text_body.split("\n"):
            if not line.strip():
                html_lines.append("<br>")
            else:
                html_lines.append(f"<p>{line}</p>")
        html_lines.append("</body></html>")
        return "\n".join(html_lines)

    def get_notification_history(
        self, user_id: str, limit: int = 50
    ) -> List[Notification]:
        user_notifications = [
            n for n in self._notifications
            if n.recipient == user_id or (
                n.metadata.get("user_id") == user_id
            )
        ]
        sorted_notifications = sorted(
            user_notifications,
            key=lambda n: n.created_at,
            reverse=True,
        )
        return sorted_notifications[:limit]