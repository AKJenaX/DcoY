"""Reusable section content and navigation data for the DcoY marketing experience."""

from typing import List, Dict, Any


def get_marketing_nav_items() -> List[Dict[str, Any]]:
    """Return the marketing navigation structure used by the landing experience."""
    return [
        {"id": "landing", "label": "Home", "href": "#landing"},
        {"id": "platform", "label": "Platform", "href": "#platform"},
        {"id": "solutions", "label": "Solutions", "href": "#solutions"},
        {"id": "resources", "label": "Resources", "href": "#resources"},
        {"id": "pricing", "label": "Pricing", "href": "#pricing"},
        {"id": "about", "label": "About", "href": "#about"},
        {"id": "contact", "label": "Contact", "href": "#contact"},
    ]


def get_platform_cards() -> List[Dict[str, Any]]:
    """Return platform capability cards for the Bento layout."""
    return [
        {"title": "AI Security Analyst", "description": "Autonomous triage, reasoning, and incident summarization with explainable evidence.", "badge": "Live reasoning"},
        {"title": "Threat Intelligence", "description": "Context-rich adversary intel, IOC enrichment, and MITRE mapping in one workspace.", "badge": "Adaptive feeds"},
        {"title": "Threat Hunting", "description": "Rapid pivots into suspicious activity with behavioral and graph-based hunting flows.", "badge": "Proactive"},
        {"title": "Detection Engineering", "description": "Design, validate, and tune detections with AI-assisted rule quality scoring.", "badge": "Trusted"},
        {"title": "Investigations", "description": "Case management and timeline reconstruction for fast coordinated response.", "badge": "Collaborative"},
        {"title": "Executive Intelligence", "description": "Leadership-ready reporting on resilience, risk posture, and response efficiency.", "badge": "Board-ready"},
        {"title": "MITRE ATT&CK", "description": "Coverage mapping and gap analysis aligned to the adversary playbook.", "badge": "Coverage"},
        {"title": "SOAR Automation", "description": "Orchestrated actions and response playbooks with secure guardrails.", "badge": "Coming soon"},
    ]


def get_trust_stats() -> List[Dict[str, Any]]:
    """Return trust metrics for the marketing landing page."""
    return [
        {"value": "4.9/5", "label": "Analyst satisfaction"},
        {"value": "99.99%", "label": "Platform uptime"},
        {"value": "24/7", "label": "AI coverage"},
        {"value": "100+", "label": "Integrations"},
    ]


def get_quotes() -> List[Dict[str, Any]]:
    """Return analyst quotes for trust section."""
    return [
        {"quote": "DcoY gives our SOC an always-on analyst that translates noisy telemetry into decisive action.", "author": "CISO, Global Fintech"},
        {"quote": "The evidence trail and MITRE mapping make every investigation easier to communicate and defend.", "author": "Senior Detection Engineer, Healthcare"},
    ]
