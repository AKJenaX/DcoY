"""Tests for Sprint 4.9.1: Rule Validation, Metrics, and Quality services."""

import json
import pytest
from app.services.rule_validator import RuleValidator
from app.services.rule_metrics import RuleMetrics


class TestRuleValidator:
    """Test suite for detection rule validation service."""

    def setup_method(self):
        self.validator = RuleValidator()

    def test_valid_rule_passes(self):
        data = {
            "name": "SSH Brute Force Alert",
            "description": "Detect repeated SSH login failures",
            "severity": "High",
            "category": "Brute Force",
            "mitre_technique": "T1110 - Brute Force",
            "detection_logic": '{"event_type": "ssh_bruteforce"}',
            "threshold": 5,
            "time_window": 60,
        }
        is_valid, errors = self.validator.validate(data)
        assert is_valid is True
        assert len([e for e in errors if e["severity"] == "error"]) == 0

    def test_missing_name_fails(self):
        data = {"name": "", "description": "Test", "detection_logic": '{"a": 1}'}
        is_valid, errors = self.validator.validate(data)
        assert is_valid is False
        assert any(e["field"] == "name" for e in errors)

    def test_missing_description_fails(self):
        data = {"name": "Test", "description": "", "detection_logic": '{"a": 1}'}
        is_valid, errors = self.validator.validate(data)
        assert is_valid is False
        assert any(e["field"] == "description" for e in errors)

    def test_missing_detection_logic_fails(self):
        data = {"name": "Test", "description": "A rule", "detection_logic": ""}
        is_valid, errors = self.validator.validate(data)
        assert is_valid is False
        assert any(e["field"] == "detection_logic" for e in errors)

    def test_invalid_json_detection_logic_fails(self):
        data = {"name": "Test", "description": "A rule", "detection_logic": "not json"}
        is_valid, errors = self.validator.validate(data)
        assert is_valid is False
        assert any(e["field"] == "detection_logic" and "invalid JSON" in e["message"] for e in errors)

    def test_empty_json_object_warns(self):
        data = {"name": "Test", "description": "A rule", "detection_logic": "{}"}
        is_valid, errors = self.validator.validate(data)
        assert is_valid is True  # Warnings don't block
        assert any(e["severity"] == "warning" for e in errors)

    def test_invalid_severity_fails(self):
        data = {
            "name": "Test", "description": "A rule",
            "detection_logic": '{"a": 1}', "severity": "Critical"
        }
        is_valid, errors = self.validator.validate(data)
        assert is_valid is False

    def test_duplicate_name_fails(self):
        data = {"name": "SSH Scanner", "description": "A rule", "detection_logic": '{"a": 1}'}
        is_valid, errors = self.validator.validate(data, existing_names=["SSH Scanner"])
        assert is_valid is False
        assert any(e["field"] == "name" and "already exists" in e["message"] for e in errors)

    def test_threshold_zero_fails(self):
        data = {
            "name": "Test", "description": "A rule",
            "detection_logic": '{"a": 1}', "threshold": 0
        }
        is_valid, errors = self.validator.validate(data)
        assert is_valid is False
        assert any(e["field"] == "threshold" for e in errors)

    def test_time_window_too_small_fails(self):
        data = {
            "name": "Test", "description": "A rule",
            "detection_logic": '{"a": 1}', "time_window": 2
        }
        is_valid, errors = self.validator.validate(data)
        assert is_valid is False
        assert any(e["field"] == "time_window" for e in errors)

    def test_unknown_mitre_warns(self):
        data = {
            "name": "Test", "description": "A rule",
            "detection_logic": '{"a": 1}',
            "mitre_technique": "T9999 - Not Real"
        }
        is_valid, errors = self.validator.validate(data)
        assert is_valid is True
        assert any(e["field"] == "mitre_technique" and e["severity"] == "warning" for e in errors)

    def test_unknown_category_warns(self):
        data = {
            "name": "Test", "description": "A rule",
            "detection_logic": '{"a": 1}',
            "category": "Space Invasion"
        }
        is_valid, errors = self.validator.validate(data)
        assert is_valid is True
        assert any(e["field"] == "category" and e["severity"] == "warning" for e in errors)


class TestRuleMetrics:
    """Test suite for rule metrics service."""

    def setup_method(self):
        self.metrics = RuleMetrics()
        self.metrics.clear_metrics()

    def test_initial_metrics_are_zero(self):
        m = self.metrics.get_metrics(1)
        assert m["executions"] == 0
        assert m["matches"] == 0
        assert m["health_score"] >= 0

    def test_record_execution_increments_counters(self):
        self.metrics.record_execution(1, matched_count=3, duration_ms=5.0)
        m = self.metrics.get_metrics(1)
        assert m["executions"] == 1
        assert m["matches"] == 3
        assert m["trigger_count"] == 1

    def test_cache_hit_tracking(self):
        self.metrics.record_execution(1, matched_count=0, duration_ms=1.0, cache_hit=True)
        m = self.metrics.get_metrics(1)
        assert m["cache_hits"] == 1
        assert m["cache_hit_ratio"] == 1.0

    def test_failed_evaluations(self):
        self.metrics.record_execution(1, matched_count=0, duration_ms=1.0, failed=True)
        m = self.metrics.get_metrics(1)
        assert m["failed_evaluations"] == 1

    def test_health_score_bounded(self):
        for i in range(50):
            self.metrics.record_execution(1, matched_count=1, duration_ms=1.0)
        m = self.metrics.get_metrics(1)
        assert 0.0 <= m["health_score"] <= 1.0

    def test_get_all_metrics(self):
        self.metrics.record_execution(1, matched_count=1, duration_ms=1.0)
        self.metrics.record_execution(2, matched_count=0, duration_ms=2.0)
        all_m = self.metrics.get_all_metrics()
        assert len(all_m) == 2

    def test_coverage_stats(self):
        rules = [
            {"mitre_technique": "T1110 - Brute Force", "category": "Brute Force", "severity": "High"},
            {"mitre_technique": "T1046 - Network Scanning", "category": "Port Scan", "severity": "Medium"},
        ]
        stats = self.metrics.get_coverage_stats(rules)
        assert stats["total_rules"] == 2
        assert stats["mitre_covered"] == 2
        assert stats["mitre_coverage_pct"] > 0
        assert len(stats["uncovered_tactics"]) > 0
        assert stats["severity_distribution"]["High"] == 1
        assert stats["severity_distribution"]["Medium"] == 1

    def test_coverage_stats_empty_rules(self):
        stats = self.metrics.get_coverage_stats([])
        assert stats["total_rules"] == 0
        assert stats["mitre_covered"] == 0
