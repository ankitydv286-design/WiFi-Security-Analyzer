
import ipaddress
import platform
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from scanner.wifi_info import _get_local_ip
from config import SCAN_TIMEOUT_SECONDS


MAX_WORKERS = 64


def _get_subnet():
    ip = _get_local_ip()

    try:
        network = ipaddress.ip_network(f"{ip}/24", strict=False)
        return network
    except ValueError:
        return None



def _ping(ip):
    is_windows = platform.system() == "Windows"

    try:
        result = subprocess.run(
            [
                "ping",
                "-n" if is_windows else "-c",
                "1",
                "-w" if is_windows else "-W",
                "1000" if is_windows else "1",
                str(ip)
            ],
            capture_output=True,
            text=True,
            timeout=3,
            errors="replace"
        )

        output = result.stdout.lower()

        # Accept only an actual successful reply.
        if is_windows:
            return (
                result.returncode == 0
                and "ttl=" in output
                and "reply from" in output
            )

        return result.returncode == 0 and "bytes from" in output

    except (OSError, subprocess.SubprocessError):
        return False


  


def _get_mac_from_arp(ip):
    try:
        result = subprocess.run(
            ["arp", "-a", str(ip)],
            capture_output=True,
            text=True,
            timeout=3,
            errors="replace"
        )

        match = re.search(
            r"([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})",
            result.stdout,
            re.IGNORECASE
        )

        return (
            match.group(1).replace("-", ":").upper()
            if match else "Unavailable"
        )

    except (OSError, subprocess.SubprocessError):
        return "Unavailable"


def _inspect_device(ip):
    if not _ping(ip):
        return None

    try:
        hostname = socket.gethostbyaddr(str(ip))[0]
    except (socket.herror, socket.gaierror, OSError):
        hostname = "Unknown device"

    return {
        "ip_address": str(ip),
        "hostname": hostname,
        "mac_address": _get_mac_from_arp(ip),
        "status": "Online"
    }


def scan_local_network():
    network = _get_subnet()

    if network is None:
        return []

    # Limit scanning to a maximum of 256 addresses.
    if network.num_addresses > 256:
        network = ipaddress.ip_network(
            f"{_get_local_ip()}/24",
            strict=False
        )

    devices = []

    # Scan multiple addresses simultaneously.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = {
            executor.submit(_inspect_device, ip): ip
            for ip in network.hosts()
        }

        for future in as_completed(futures):
            try:
                device = future.result()

                if device:
                    devices.append(device)

            except Exception:
                continue

    # Keep results in IP address order.
    devices.sort(
        key=lambda device: ipaddress.ip_address(
            device["ip_address"]
        )
    )

    return devices
