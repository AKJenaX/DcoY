"""
Very simple port connectivity test
"""
import socket
import sys

def test_port(host, port):
    """Test if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            return True, "Port is open"
        else:
            return False, f"Connection refused (errno {result})"
    except socket.timeout:
        return False, "Timeout - port not responding"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        sock.close()

# Test different addresses
test_addresses = [
    ("127.0.0.1", 8000),
    ("localhost", 8000),
    ("0.0.0.0", 8000),
]

print("Testing port connectivity:\n")
for host, port in test_addresses:
    success, message = test_port(host, port)
    status = "✓" if success else "✗"
    print(f"{status} {host}:{port} - {message}")
