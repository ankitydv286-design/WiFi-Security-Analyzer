
import psutil
import time

_previous = None


def format_speed(bytes_per_second):
    units = ["B/s", "KB/s", "MB/s", "GB/s"]

    speed = max(0, bytes_per_second)
    index = 0

    while speed >= 1024 and index < len(units) - 1:
        speed /= 1024
        index += 1

    return f"{speed:.2f} {units[index]}"


def get_network_usage():
    global _previous

    current = psutil.net_io_counters()
    now = time.perf_counter()

    upload_speed = 0
    download_speed = 0

    if _previous is not None:
        old_time, old_sent, old_recv = _previous

        elapsed = max(now - old_time, 0.001)

        upload_speed = max(
            0, (current.bytes_sent - old_sent) / elapsed
        )

        download_speed = max(
            0, (current.bytes_recv - old_recv) / elapsed
        )

    _previous = (
        now,
        current.bytes_sent,
        current.bytes_recv
    )

    return {
        "bytes_sent_total": current.bytes_sent,
        "bytes_received_total": current.bytes_recv,
        "upload_bytes_per_sec": round(upload_speed, 2),
        "download_bytes_per_sec": round(download_speed, 2),
        "upload_formatted": format_speed(upload_speed),
        "download_formatted": format_speed(download_speed),
        "note": "Measures total system network interface traffic, not internet speed."
    }
