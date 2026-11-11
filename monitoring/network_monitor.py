
import socket
import time
from datetime import datetime


def check_connection(host, port=443, timeout=3):
    started = time.perf_counter()

    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency = round(
                (time.perf_counter() - started) * 1000, 2
            )

        return {
            "status": "Online",
            "latency_ms": latency,
            "host": host,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except (socket.timeout, OSError):
        return {
            "status": "Offline",
            "latency_ms": None,
            "host": host,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def get_network_status():
    # Check connectivity through two independent endpoints.
    hosts = [
        ("1.1.1.1", 443),
        ("8.8.8.8", 443)
    ]

    results = []

    for host, port in hosts:
        results.append(
            check_connection(host, port)
        )

    online_results = [
        result for result in results
        if result["status"] == "Online"
    ]

    if online_results:
        latencies = [
            result["latency_ms"]
            for result in online_results
        ]

        average_latency = round(
            sum(latencies) / len(latencies), 2
        )

        status = "Online"
    else:
        average_latency = None
        status = "Offline"

    return {
        "status": status,
        "latency_ms": average_latency,
        "successful_checks": len(online_results),
        "total_checks": len(results),
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "details": results
    }
