"""Event simulator for DcoY - sends synthetic threat events to the /api/ingest endpoint."""

import requests
import random
import time
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://127.0.0.1:8000/api/ingest"
INTERVAL_SECONDS = 2  # Send events every 2 seconds
EVENTS_PER_BATCH = 3  # Number of events per batch

# Sample PUBLIC IP addresses (simulating internet-origin attacks)
# Using a mixed set so public geolocation APIs can return map coordinates.
SAMPLE_IPS = [
    "8.8.8.8",         # Google DNS (US)
    "1.1.1.1",         # Cloudflare DNS (global)
    "9.9.9.9",         # Quad9 DNS
    "208.67.222.222",  # OpenDNS
    "151.101.1.69",    # Fastly edge
    "104.16.132.229",  # Cloudflare edge
    "13.107.21.200",   # Microsoft edge
    "52.84.0.0",       # AWS/CloudFront range representative
    "34.117.59.81",    # Google Cloud edge
    "23.45.67.89",     # Akamai-like public address example
]

# Attack patterns
ATTACK_TYPES = [
    "brute_force", "port_scan", "dos", "ssh_attempt", 
    "sql_injection", "path_traversal", "normal"
]

# Honeypot types
HONEYPOT_TYPES = ["ssh", "http", "smtp", "dns", "database"]


def generate_synthetic_event() -> dict:
    """Generate a synthetic threat event."""
    attack_type = random.choice(ATTACK_TYPES)
    is_anomaly = 1 if attack_type != "normal" else 0
    
    event = {
        "timestamp": (datetime.now() - timedelta(seconds=random.randint(0, 300))).isoformat(),
        "ip": random.choice(SAMPLE_IPS),
        "failed_logins": random.randint(0, 50) if is_anomaly else random.randint(0, 5),
        "port_attempts": random.randint(0, 100) if is_anomaly else random.randint(0, 10),
        "request_rate": random.uniform(0, 500) if is_anomaly else random.uniform(0, 100),
        "attack_type": attack_type,
        "honeypot_type": random.choice(HONEYPOT_TYPES),
        "is_anomaly": is_anomaly,
        "severity": "high" if is_anomaly else "low",
        "response_action": "blocked" if is_anomaly else "allowed"
    }
    
    return event


def send_batch(events: list) -> bool:
    """Send a batch of events to the ingest endpoint."""
    try:
        payload = {"data": events}
        
        response = requests.post(
            API_URL,
            json=payload,
            timeout=10,
            verify=False
        )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(
            f"✓ Sent {result.get('count', 0)} events | "
            f"Total in store: {result.get('total_in_store', 0)}"
        )
        
        return True
        
    except requests.exceptions.ConnectionError:
        logger.error(f"✗ Connection failed. Is backend running at {API_URL}?")
        return False
    except requests.exceptions.Timeout:
        logger.error(f"✗ Request timeout. Backend may be slow.")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Request failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error: {str(e)}")
        return False


def main():
    """Main simulator loop."""
    logger.info(f"DcoY Event Simulator")
    logger.info(f"Target: {API_URL}")
    logger.info(f"Interval: {INTERVAL_SECONDS} seconds")
    logger.info(f"Events per batch: {EVENTS_PER_BATCH}")
    logger.info("Press Ctrl+C to stop\n")
    
    # Wait for user confirmation
    input("Press Enter to start sending events...")
    
    batch_count = 0
    total_events = 0
    
    try:
        while True:
            # Generate batch of events
            events = [generate_synthetic_event() for _ in range(EVENTS_PER_BATCH)]
            
            # Send batch
            if send_batch(events):
                batch_count += 1
                total_events += len(events)
                
                # Show summary every 10 batches
                if batch_count % 10 == 0:
                    logger.info(f"📊 Summary: {batch_count} batches, {total_events} total events sent")
            
            # Wait before next batch
            time.sleep(INTERVAL_SECONDS)
    
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Simulator stopped")
        logger.info(f"📈 Final stats: {batch_count} batches, {total_events} events sent")


if __name__ == "__main__":
    main()
