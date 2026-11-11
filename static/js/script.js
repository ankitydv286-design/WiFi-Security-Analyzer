const $ = (id) => document.getElementById(id);
let chart;
const history = { download: [], upload: [], labels: [] };

function formatRate(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return "0 B/s";
  const units = ["B/s", "KB/s", "MB/s", "GB/s"];
  let value = bytes, index = 0;
  while (value >= 1024 && index < units.length - 1) { value /= 1024; index++; }
  return `${value.toFixed(1)} ${units[index]}`;
}
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  })[char]);
}
function showToast(message) {
  $("toast").textContent = message;
  $("toast").classList.add("show");
  setTimeout(() => $("toast").classList.remove("show"), 2800);
}
function renderWifi(wifi) {
  $("wifiName").textContent = wifi.ssid || "SSID unavailable";
  $("wifiSignal").textContent = wifi.signal || "—";
  const fields = [
    ["Network name (SSID)", wifi.ssid], ["Local IP address", wifi.local_ip],
    ["Default gateway", wifi.gateway], ["Authentication", wifi.authentication],
    ["Encryption cipher", wifi.encryption], ["Radio type", wifi.radio],
    ["Computer name", wifi.hostname], ["Operating system", wifi.platform]
  ];
  $("wifiDetails").innerHTML = fields.map(([label,value]) =>
    `<div class="info-item"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value || "Unavailable")}</strong></div>`
  ).join("");
}
function renderSecurity(security) {
  $("securityScore").textContent = `${security.score}/100`;
  $("securityGrade").textContent = security.grade;
  $("securityChecks").innerHTML = security.checks.map(check => {
    const css = check.status.toLowerCase();
    return `<div class="check-item"><span class="check-badge ${css}">${escapeHtml(check.status.toUpperCase())}</span><div><strong>${escapeHtml(check.name)}</strong><p>${escapeHtml(check.detail)}</p></div></div>`;
  }).join("");
  $("securityNote").textContent = security.note;
}
function renderDevices(devices) {
  $("deviceCount").textContent = devices.length;
  $("scanLabel").textContent = `Updated ${new Date().toLocaleTimeString()}`;
  $("deviceTable").innerHTML = devices.length ? devices.map(device =>
    `<tr><td>${escapeHtml(device.hostname)}</td><td>${escapeHtml(device.ip_address)}</td><td>${escapeHtml(device.mac_address)}</td><td><span class="status-pill">● ${escapeHtml(device.status)}</span></td></tr>`
  ).join("") : `<tr><td colspan="4" class="empty">No responding devices found. Check your local network and firewall settings.</td></tr>`;
}
function renderLogs(logs) {
  $("alertList").innerHTML = logs.length ? logs.map(log => {
    const level = log.severity === "High" ? "risk" : "review";
    return `<div class="alert-row"><span class="alert-level ${level}">${escapeHtml(log.severity)}</span><div><strong>${escapeHtml(log.title)}</strong><p>${escapeHtml(log.description)} · ${escapeHtml(log.timestamp)}</p></div></div>`;
  }).join("") : `<div class="empty">No security alerts recorded. This does not mean the network is guaranteed secure.</div>`;
}
function setupChart() {
  if (chart) return;
  const ctx = $("trafficChart").getContext("2d");
  chart = new Chart(ctx, {
    type: "line",
    data: { labels: history.labels, datasets: [
      {label:"Download",data:history.download,tension:.35,borderWidth:2},
      {label:"Upload",data:history.upload,tension:.35,borderWidth:2}
    ]},
    options: {responsive:true,plugins:{legend:{labels:{color:"#aab8d0"}}},
      scales:{x:{ticks:{color:"#8493ad"},grid:{color:"#25324a"}},
      y:{ticks:{color:"#8493ad"},grid:{color:"#25324a"}}}}
  });
}
function renderUsage(usage) {
  const down = usage.download_bytes_per_sec || 0;
  const up = usage.upload_bytes_per_sec || 0;
  $("downloadSpeed").textContent = formatRate(down);
  $("uploadSpeed").textContent = formatRate(up);
  setupChart();
  history.labels.push(new Date().toLocaleTimeString());
  history.download.push(Math.round(down / 1024));
  history.upload.push(Math.round(up / 1024));
  if (history.labels.length > 12) {
    history.labels.shift(); history.download.shift(); history.upload.shift();
  }
  chart.update();
}
async function refreshDashboard() {
  const button = $("refreshButton");
  button.disabled = true;
  button.textContent = "Scanning...";
  try {
    const response = await fetch("/api/overview");
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const data = await response.json();
    renderWifi(data.wifi);
    renderSecurity(data.security);
    renderDevices(data.devices);
    renderUsage(data.usage);
    renderLogs(data.logs);
    $("networkStatus").textContent = data.network.status;
    $("latency").textContent = data.network.latency_ms === null
      ? "No response from connectivity check" : `${data.network.latency_ms} ms response time`;
  } catch (error) {
    showToast(`Could not load dashboard: ${error.message}`);
    $("networkStatus").textContent = "Unavailable";
  } finally {
    button.disabled = false;
    button.textContent = "↻ Refresh scan";
  }
}
$("refreshButton").addEventListener("click", refreshDashboard);
refreshDashboard();
setInterval(refreshDashboard, 30000);
