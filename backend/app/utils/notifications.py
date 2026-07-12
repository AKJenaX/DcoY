"""Modular notification adapter service for forwarding event updates to remote alert networks."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class NotificationAdapter(ABC):
    """Abstract interface defining required methods for external alert adapters."""

    @abstractmethod
    def send(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Sends serialized webhook payload to third-party integrations."""
        pass


class SlackNotificationAdapter(NotificationAdapter):
    """Adapter to format and deliver payloads to Slack webhook endpoints."""

    def send(self, event_name: str, payload: Dict[str, Any]) -> None:
        logger.info(
            f"[SLACK ADAPTER] Forwarding event '{event_name}' - "
            f"Payload: {payload.get('message', 'No details')}"
        )


class TeamsNotificationAdapter(NotificationAdapter):
    """Adapter to format and deliver payloads to MS Teams webhooks."""

    def send(self, event_name: str, payload: Dict[str, Any]) -> None:
        logger.info(
            f"[TEAMS ADAPTER] Posting adaptive card for '{event_name}' - "
            f"Message: {payload.get('message')}"
        )


class PagerDutyNotificationAdapter(NotificationAdapter):
    """Adapter to trigger incidents in PagerDuty services."""

    def send(self, event_name: str, payload: Dict[str, Any]) -> None:
        severity = payload.get("severity", "info").upper()
        logger.info(
            f"[PAGERDUTY ADAPTER] Triggering critical incident for '{event_name}' - "
            f"Severity: {severity} | Details: {payload.get('message')}"
        )


class EmailNotificationAdapter(NotificationAdapter):
    """Adapter to dispatch alert emails to security distribution lists."""

    def send(self, event_name: str, payload: Dict[str, Any]) -> None:
        logger.info(
            f"[EMAIL ADAPTER] Dispatched alert email for '{event_name}' to soc-alerts@dcoy.internal"
        )


class NotificationEngine:
    """Consolidates registered alerts and coordinates multi-adapter delivery loops."""

    def __init__(self) -> None:
        self.adapters: List[NotificationAdapter] = []
        
        # Self-register default adapters
        self.register_adapter(SlackNotificationAdapter())
        self.register_adapter(TeamsNotificationAdapter())
        self.register_adapter(PagerDutyNotificationAdapter())
        self.register_adapter(EmailNotificationAdapter())

    def register_adapter(self, adapter: NotificationAdapter) -> None:
        self.adapters.append(adapter)

    def trigger(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Triggers the alert dissemination loop across all registered adapters."""
        logger.info(f"Notification engine triggered: {event_name}")
        for adapter in self.adapters:
            try:
                adapter.send(event_name, payload)
            except Exception as e:
                logger.error(
                    f"Notification delivery failed on adapter {type(adapter).__name__}: {str(e)}"
                )


# Instantiated global service engine
notification_engine = NotificationEngine()
