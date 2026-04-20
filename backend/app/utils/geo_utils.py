"""Geolocation utilities for IP address mapping."""

import requests
import logging
from typing import Dict, Any
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, wait
import threading
import ipaddress

logger = logging.getLogger(__name__)

# In-memory cache for geolocation results to avoid repeated API calls
_geo_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()

# Thread pool for parallel geolocation lookups
_executor = ThreadPoolExecutor(max_workers=5)


def _unknown_location(ip: str) -> Dict[str, Any]:
    """Return a consistent unknown-location payload."""
    return {
        "ip": ip,
        "lat": None,
        "lon": None,
        "country": "Unknown",
        "city": "Unknown",
        "region": "Unknown"
    }


def _is_non_public_ip(ip: str) -> bool:
    """Skip geolocation calls for private/local/reserved addresses."""
    try:
        parsed = ipaddress.ip_address(ip)
        return (
            parsed.is_private
            or parsed.is_loopback
            or parsed.is_reserved
            or parsed.is_multicast
            or parsed.is_link_local
            or parsed.is_unspecified
        )
    except ValueError:
        # Not a valid IP literal; avoid external lookup
        return True


def _get_single_location(ip: str, timeout: int = 3) -> Dict[str, Any]:
    """
    Internal function to get a single IP location with timeout.
    
    Args:
        ip: IP address string
        timeout: Request timeout in seconds (default 3s for speed)
        
    Returns:
        Dictionary with geolocation data
    """
    if not ip or ip == "unknown":
        return _unknown_location(ip)

    # Local/private IPs are not geolocatable via public IP providers.
    if _is_non_public_ip(ip):
        return _unknown_location(ip)
    
    try:
        # Use ip-api.com free tier with shorter timeout for responsiveness
        response = requests.get(
            f"http://ip-api.com/json/{ip}",
            timeout=timeout,
            params={"fields": "lat,lon,country,city,region,status"}
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            logger.debug(f"Geolocation found for {ip}: {data.get('country')}")
            return {
                "ip": ip,
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown")
            }
        else:
            logger.debug(f"Geolocation API returned error for {ip}")
            return _unknown_location(ip)
    
    except requests.exceptions.Timeout:
        logger.warning(f"Geolocation timeout for {ip} (timeout={timeout}s)")
        return _unknown_location(ip)
    
    except Exception as e:
        logger.warning(f"Error getting geolocation for {ip}: {str(e)}")
        return _unknown_location(ip)


@lru_cache(maxsize=1000)
def get_ip_location(ip: str) -> Dict[str, Any]:
    """
    Get geolocation data for an IP address using ip-api.com with caching.
    
    Args:
        ip: IP address string
        
    Returns:
        Dictionary with geolocation data (lat, lon, country, city)
        Returns empty/default values on error
    """
    # Check cache first (thread-safe)
    with _cache_lock:
        if ip in _geo_cache:
            logger.debug(f"Cache hit for {ip}")
            return _geo_cache[ip]
    
    # Get fresh location
    result = _get_single_location(ip, timeout=3)
    
    # Cache the result before returning (thread-safe)
    with _cache_lock:
        _geo_cache[ip] = result
    
    return result


def batch_get_locations(ips: list) -> Dict[str, Dict[str, Any]]:
    """
    Get locations for multiple IPs in parallel (with caching and timeout).
    
    Args:
        ips: List of IP addresses
        
    Returns:
        Dictionary mapping IP to location data
    """
    results = {}
    
    # Check which IPs are already cached
    uncached_ips = []
    with _cache_lock:
        for ip in ips:
            if ip in _geo_cache:
                results[ip] = _geo_cache[ip]
            else:
                uncached_ips.append(ip)
    
    # Fetch uncached IPs in parallel with futures
    if uncached_ips:
        # Keep a hard cap so /explain remains responsive under heavy load.
        capped_ips = uncached_ips[:20]
        futures = {
            _executor.submit(_get_single_location, ip, timeout=2): ip
            for ip in capped_ips
        }

        done, not_done = wait(futures.keys(), timeout=6)

        for future in done:
            ip = futures[future]
            try:
                result = future.result()
            except Exception as e:
                logger.warning(f"Failed to get location for {ip}: {str(e)}")
                result = _unknown_location(ip)

            results[ip] = result
            with _cache_lock:
                _geo_cache[ip] = result

        # Return graceful fallback for timed-out lookups instead of raising.
        for future in not_done:
            ip = futures[future]
            future.cancel()
            logger.warning(f"Geolocation lookup timed out for {ip}")
            fallback = _unknown_location(ip)
            results[ip] = fallback
            with _cache_lock:
                _geo_cache[ip] = fallback

        # Any IPs beyond cap get immediate fallback to keep request latency bounded.
        for ip in uncached_ips[20:]:
            fallback = _unknown_location(ip)
            results[ip] = fallback
            with _cache_lock:
                _geo_cache[ip] = fallback
    
    return results
