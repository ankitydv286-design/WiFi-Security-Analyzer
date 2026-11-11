# NetShield — Wi-Fi Security Analyzer & Network Monitoring System

A local-first educational cybersecurity dashboard for viewing Wi-Fi connection details, discovering responding devices on your own local subnet, checking basic Wi-Fi security configuration, and monitoring network-interface throughput.

## Features

- Windows Wi-Fi details: SSID, signal, authentication and cipher (where Windows exposes them).
- Local IPv4 and default gateway detection.
- Basic local-subnet device discovery using ping and ARP.
- Basic WPA2/WPA3/open-authentication configuration review.
- Connectivity and response-time check.
- Device interface upload/download throughput estimates.
- SQLite history for discovered devices, monitoring checks and security alerts.
- Flask JSON API and responsive dashboard.

## Requirements

- Windows 10/11 recommended.
- Python 3.10 or newer.
- VS Code (recommended).
- Internet connection for the Chart.js CDN and connectivity check.
- Device discovery works best when run on a network you own or have explicit permission to assess.

## Setup (Windows PowerShell or VS Code terminal)

1. Open this project folder in VS Code.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv venv
   .\\venv\\Scripts\\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt terminal and run:

   ```cmd
   venv\\Scripts\\activate.bat
   ```

3. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Start the application:

   ```powershell
   py app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

## API routes

| Route | Description |
|---|---|
| `/api/health` | Application health check |
| `/api/overview` | Combined dashboard data |
| `/api/wifi` | Local Wi-Fi information |
| `/api/devices` | Local subnet discovery |
| `/api/security` | Basic configuration review |
| `/api/monitoring` | Connectivity status |
| `/api/speed` | Network interface throughput |
| `/api/logs` | Recent security logs |

## Important limitations

- This is a defensive learning and visibility tool, not a penetration-testing suite.
- Device discovery uses ICMP ping and ARP. Firewalls, sleeping devices, guest networks and client isolation can prevent discovery. A device not shown is not necessarily disconnected.
- The subnet discovery currently assumes a typical IPv4 `/24` network. Adjust the scanner for a different subnet before use.
- The dashboard's traffic rates are device network-interface throughput, not an internet bandwidth speed test.
- Windows `netsh` output differs by language and adapter. Some fields may display as unavailable.
- The security score is a simple educational heuristic. It is not a certified security rating and cannot prove a Wi-Fi network is secure.
- The app binds to `127.0.0.1` so the dashboard is accessible only from the same computer by default.
- Use only on networks and devices you own or are authorized to monitor.

## Project structure

```text
scanner/       Wi-Fi information, device discovery, security review
monitoring/    Connectivity and interface throughput
database/      SQLite storage
templates/     Flask HTML template
static/        CSS and JavaScript dashboard
reports/       Reserved for exported reports
tests/         Reserved for automated tests
```

## Suggested next improvements

1. Add configurable subnet selection.
2. Add a proper test suite.
3. Add CSV/PDF report export.
4. Add background polling rather than scanning during each dashboard refresh.
5. Add authenticated access before enabling access from other computers.
6. Add unit tests for platform-specific parsing and security checks.
