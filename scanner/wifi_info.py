import platform
import re
import socket
import subprocess
import psutil

def _run_windows_command(command):
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=8,
            encoding="utf-8", errors="replace", shell=False
        )
        return completed.stdout if completed.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""

def _get_windows_wifi_details():
    if platform.system() != "Windows":
        return {}
    output = _run_windows_command(["netsh", "wlan", "show", "interfaces"])
    details = {}
    patterns = {
        "ssid": r"^\s*SSID\s*:\s*(.+)$",
        "signal": r"^\s*Signal\s*:\s*(\d+%)",
        "authentication": r"^\s*Authentication\s*:\s*(.+)$",
        "encryption": r"^\s*Cipher\s*:\s*(.+)$",
        "radio": r"^\s*Radio type\s*:\s*(.+)$",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output, re.MULTILINE | re.IGNORECASE)
        if match:
            details[key] = match.group(1).strip()
    return details

def _get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "Unavailable"
    finally:
        sock.close()


def _get_gateway():
    if platform.system() == "Windows":
        output = _run_windows_command(["ipconfig"])

        lines = output.splitlines()

        for index, line in enumerate(lines):
            if "Default Gateway" in line:
                # Check the current line and the next lines
                for gateway_line in lines[index:index + 3]:
                    match = re.search(
                        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                        gateway_line
                    )
                    if match:
                        return match.group(0)

        return "Unavailable"

    return "Check system network settings"

def get_wifi_info():
    details = _get_windows_wifi_details()
    interfaces = psutil.net_if_stats()
    active = [name for name, stats in interfaces.items() if stats.isup]
    return {
        "hostname": socket.gethostname(),
        "local_ip": _get_local_ip(),
        "gateway": _get_gateway(),
        "ssid": details.get("ssid", "Unavailable"),
        "signal": details.get("signal", "Unavailable"),
        "authentication": details.get("authentication", "Unavailable"),
        "encryption": details.get("encryption", "Unavailable"),
        "radio": details.get("radio", "Unavailable"),
        "active_interfaces": active,
        "platform": platform.system()
    }
