
from flask import Flask, jsonify, render_template
from werkzeug.exceptions import HTTPException

from scanner.wifi_info import get_wifi_info
from scanner.network_scanner import scan_local_network
from scanner.security_analyzer import analyze_security

from monitoring.network_monitor import get_network_status
from monitoring.speed_monitor import get_network_usage

from database.db import (
    init_db,
    save_devices,
    save_monitoring,
    save_security_alerts,
    get_recent_logs
)


app = Flask(__name__)


@app.get("/")
def dashboard():
    return render_template("index.html")


@app.get("/api/overview")
def overview():
    wifi = get_wifi_info()
    status = get_network_status()
    usage = get_network_usage()
    devices = scan_local_network()
    security = analyze_security(wifi)

    save_devices(devices)
    save_monitoring(status)
    save_security_alerts(security["alerts"])

    return jsonify({
        "wifi": wifi,
        "network": status,
        "usage": usage,
        "devices": devices,
        "security": security,
        "logs": get_recent_logs()
    })


@app.get("/api/wifi")
def wifi():
    return jsonify(get_wifi_info())


@app.get("/api/devices")
def devices():
    result = scan_local_network()
    save_devices(result)

    return jsonify({
        "devices": result,
        "count": len(result)
    })


@app.get("/api/security")
def security():
    result = analyze_security(get_wifi_info())
    save_security_alerts(result["alerts"])

    return jsonify(result)


@app.get("/api/monitoring")
def monitoring():
    result = get_network_status()
    save_monitoring(result)

    return jsonify(result)


@app.get("/api/speed")
def speed():
    return jsonify(get_network_usage())


@app.get("/api/logs")
def logs():
    return jsonify(get_recent_logs())


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "application": "Wi-Fi Security Analyzer"
    })


@app.errorhandler(HTTPException)
def handle_http_error(error):
    return jsonify({
        "error": error.name,
        "message": error.description
    }), error.code


@app.errorhandler(Exception)
def handle_server_error(error):
    app.logger.exception("Unexpected application error")

    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected server error occurred."
    }), 500


if __name__ == "__main__":
    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
