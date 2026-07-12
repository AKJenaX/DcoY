"""Pydantic V2 data models for request/response validation and typing."""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Sequence


class EventModel(BaseModel):
    """Represents a single raw or processed security event log."""
    ip: str = Field(..., description="IP Address of the event source")
    failed_logins: float = Field(default=0.0, description="Number of failed login attempts")
    port_attempts: float = Field(default=0.0, description="Number of port scan or recon attempts")
    request_rate: float = Field(default=0.0, description="Network / HTTP request rate per unit time")
    timestamp: Optional[str] = Field(default=None, description="ISO format timestamp")
    time: Optional[str] = Field(default=None, description="Legacy raw time string")
    
    # Enrichment fields added by detection pipeline
    is_anomaly: Optional[int] = Field(default=None, description="Isolation Forest anomaly flag (1 = anomaly, 0 = normal)")
    anomaly_score: Optional[float] = Field(default=None, description="Isolation Forest continuous anomaly decision function score")
    attack_type: Optional[str] = Field(default=None, description="Rule-based classification label (e.g. ssh_bruteforce, port_scan)")
    
    # Legacy deception/response fields mapping
    honeypot: Optional[str] = Field(default=None, description="Direct select_honeypot result")
    response_action: Optional[str] = Field(default=None, description="Direct select_honeypot response action")
    response_status: Optional[str] = Field(default=None, description="Direct select_honeypot response status")


class IngestPayload(BaseModel):
    """Request body for event ingestion endpoints."""
    data: List[EventModel] = Field(..., description="List of threat events to ingest")


class GeolocationInfo(BaseModel):
    """Structured geolocation information for mapping threat origins."""
    ip: str = Field(..., description="Target IP Address")
    lat: Optional[float] = Field(default=None, description="Latitude coordinate")
    lon: Optional[float] = Field(default=None, description="Longitude coordinate")
    country: str = Field(default="Unknown", description="Country name")
    city: str = Field(default="Unknown", description="City name")
    region: str = Field(default="Unknown", description="Region name")


class AgentMessageModel(BaseModel):
    """Enriched event format passed down the multi-agent pipeline."""
    event_type: str = Field(..., description="Classified attack type (e.g. ssh_bruteforce, normal)")
    severity: str = Field(..., description="ML outlier classification (high = anomaly, low = normal)")
    ip: str = Field(..., description="IP Address of the attacker")
    risk_score: float = Field(..., description="Aggregated risk score in range [0.0, 1.0]")
    risk_level: str = Field(..., description="Categorized risk bucket (high, medium, low)")
    attacker_profile: str = Field(..., description="Behavior profile (advanced, automated_tool, beginner)")
    profile_reason: str = Field(..., description="Human-readable explanation of the behavior profile")
    history_events: int = Field(default=0, description="Total history occurrences seen in feedback store")
    repeat_offender_score: int = Field(default=0, description="Number of historical high-risk flags")
    details: Dict[str, Any] = Field(..., description="Raw underlying metrics and metadata dictionary")
    user: str = Field(default="default_user", description="Analyst scope user identifier")
    
    # Deception agent outputs
    honeypot: Optional[str] = Field(default=None, description="Target honeypot environment to stand up")
    deception_action: Optional[str] = Field(default=None, description="Deceptive mitigation action description")
    deception_status: Optional[str] = Field(default=None, description="Deception deployment status (deployed/ignored)")
    deception_reason: Optional[str] = Field(default=None, description="Behavior-aligned reasoning for decoy choice")
    
    # Response agent outputs
    response_action_final: Optional[str] = Field(default=None, description="Action taken by response agent")
    response_status_final: Optional[str] = Field(default=None, description="Enforcement state of response action")
    strategy_reason: Optional[str] = Field(default=None, description="Mitigation rationale")
    
    # Reasoning agent outputs
    explanation: Optional[str] = Field(default=None, description="Natural language reasoning explanation")
    location: Optional[GeolocationInfo] = Field(default=None, description="Threat geographical coordinate data")


class DetectResponse(BaseModel):
    """Response schema for direct detection endpoints."""
    total_records: int
    anomalies_detected: int
    attack_summary: Dict[str, int]
    response_summary: Dict[str, int]
    data: Sequence[EventModel]


class AgentPipelineResponse(BaseModel):
    """Response schema for core multi-agent pipeline executions."""
    total_events: int
    high_risk: int
    medium_risk: int
    low_risk: int
    data: Sequence[AgentMessageModel]


class ExplainPipelineResponse(BaseModel):
    """Response schema for explainable AI multi-agent pipelines."""
    total_events: int
    data: Sequence[AgentMessageModel]


class IngestResponse(BaseModel):
    """Response schema for event ingestion endpoint."""
    message: str
    count: int
    total_in_store: int


class ApiDetectResponse(BaseModel):
    """Response schema for custom authenticated API detection endpoint."""
    user: str
    total_events: int
    data: Sequence[AgentMessageModel]


class ApiExplainResponse(BaseModel):
    """Response schema for custom authenticated API explanation endpoint."""
    user: str
    total_events: int
    data: Sequence[AgentMessageModel]
