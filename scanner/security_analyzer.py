
def analyze_security(wifi):
    authentication = str(
        wifi.get("authentication", "Unavailable")
    ).strip().lower()

    encryption = str(
        wifi.get("encryption", "Unavailable")
    ).strip().lower()

    ssid = wifi.get("ssid", "Unavailable")

    alerts = []
    checks = []
    score = 100

    # 1. Wi-Fi connection check
    if not ssid or ssid == "Unavailable":
        checks.append({
            "name": "Wi-Fi connection",
            "status": "Unknown",
            "detail": "Wi-Fi information is unavailable."
        })
    else:
        checks.append({
            "name": "Wi-Fi connection",
            "status": "Good",
            "detail": f"Connected network: {ssid}"
        })

    # 2. Authentication check
    if "open" in authentication:
        score -= 50

        checks.append({
            "name": "Authentication",
            "status": "Risk",
            "detail": "Open authentication detected."
        })

        alerts.append({
            "severity": "High",
            "title": "Open Wi-Fi network",
            "description": "The network appears to use open authentication."
        })

    elif "wpa3" in authentication:
        checks.append({
            "name": "Authentication",
            "status": "Good",
            "detail": "WPA3 authentication detected."
        })

    elif "wpa2" in authentication:
        checks.append({
            "name": "Authentication",
            "status": "Good",
            "detail": "WPA2 authentication detected."
        })

    elif "wpa" in authentication:
        score -= 20

        checks.append({
            "name": "Authentication",
            "status": "Review",
            "detail": "Legacy WPA authentication detected."
        })

        alerts.append({
            "severity": "Review",
            "title": "Legacy authentication",
            "description": "Consider upgrading to WPA2 or WPA3."
        })

    else:
        checks.append({
            "name": "Authentication",
            "status": "Unknown",
            "detail": "Authentication information is unavailable or unsupported."
        })

        alerts.append({
            "severity": "Review",
            "title": "Authentication could not be verified",
            "description": "Check your router's security configuration."
        })

    # 3. Encryption check
    if encryption in ("ccmp", "aes", "gcmp", "gcpm"):
        checks.append({
            "name": "Encryption",
            "status": "Good",
            "detail": f"Modern encryption cipher detected: {encryption.upper()}."
        })

    elif "tkip" in encryption or "wep" in encryption:
        score -= 35

        checks.append({
            "name": "Encryption",
            "status": "Risk",
            "detail": f"Weak or outdated encryption detected: {encryption.upper()}."
        })

        alerts.append({
            "severity": "High",
            "title": "Weak encryption detected",
            "description": "Replace WEP or TKIP with modern encryption."
        })

    else:
        checks.append({
            "name": "Encryption",
            "status": "Unknown",
            "detail": "Encryption information could not be verified."
        })

        alerts.append({
            "severity": "Review",
            "title": "Encryption could not be verified",
            "description": "Check the encryption settings on your router."
        })

    # 4. Final score
    score = max(0, min(100, score))

    if score >= 85:
        grade = "Good"
    elif score >= 70:
        grade = "Review"
    else:
        grade = "Needs attention"

    return {
        "score": score,
        "grade": grade,
        "checks": checks,
        "alerts": alerts,
        "note": (
            "This is a basic configuration assessment, "
            "not a penetration test or guarantee of network security."
        )
    }
