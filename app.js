
// Initialize Icons
lucide.createIcons();

// --- CHART INITIALIZATION ---
let history = { ax: [], ay: [], az: [], labels: [] };
const MAX_DATAPOINTS = 40;

const chart = new ApexCharts(document.querySelector("#chart"), {
    series: [
        { name: 'Accel-X', data: [] },
        { name: 'Accel-Y', data: [] },
        { name: 'Accel-Z', data: [] }
    ],
    chart: { 
        type: 'line', height: '100%', toolbar: { show: false }, 
        animations: { enabled: true, easing: 'linear', dynamicAnimation: { speed: 800 } }, 
        background: 'transparent', foreColor: '#64748b' 
    },
    stroke: { curve: 'smooth', width: 3 },
    colors: ['#38bdf8', '#fb7185', '#10b981'],
    grid: { borderColor: 'rgba(255,255,255,0.02)', strokeDashArray: 4 },
    xaxis: { labels: { show: false } },
    yaxis: { min: -2, max: 2, labels: { style: { fontSize: '10px' } } },
    legend: { show: false },
    tooltip: { theme: 'dark' }
});
chart.render();

function toggleSimulator() {
    document.getElementById('sim-panel').classList.toggle('hidden');
}

function addLog(type, msg) {
    const box = document.getElementById('logs');
    const div = document.createElement('div');
    const time = new Date().toLocaleTimeString('en-GB', { hour12: false });
    div.innerHTML = `<span class="text-slate-600">[${time}]</span> <span class="font-bold text-sky-400">${type}</span>: ${msg}`;
    box.prepend(div);
    if (box.children.length > 50) box.lastElementChild.remove();
}

async function sendSimData(mode) {
    let payload = {};
    if (mode === 'NORMAL') {
        payload = {
            gps: { latitude: 9.9312, longitude: 76.2673, satellites: 18 },
            mpu: { vibration_rms: 0.05, ax: 0.01, ay: 0.01, az: 1.0 },
            motor: { rpm: 1500, hall_detected: true },
            system: { scan_triggered: false }
        };
    } else if (mode === 'WARNING') {
        payload = {
            gps: { latitude: 9.9410, longitude: 76.2710, satellites: 12 }, // Near airport center
            mpu: { vibration_rms: 0.45, ax: 0.2, ay: 0.1, az: 0.9 },
            motor: { rpm: 3800 }
        };
    } else if (mode === 'CRITICAL') {
        payload = {
            gps: { latitude: 9.9401, longitude: 76.2701, satellites: 8 }, // Inside airport center
            mpu: { vibration_rms: 0.8, ax: 0.5, ay: -0.5, az: 0.8 },
            motor: { rpm: 200 }
        };
    } else if (mode === 'SCAN') {
        payload = { system: { scan_triggered: true } };
        addLog("SYS", "Hardware diagnostic scan triggered...");
        setTimeout(() => sendSimData('NORMAL'), 3000);
    }

    try {
        await fetch('/data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (e) { addLog("ERR", "Simulator disconnected"); }
}

async function sync() {
    try {
        const response = await fetch('/api/current');
        if (!response.ok) throw new Error("Offline");
        const d = await response.json();

        // UI Telemetry
        document.getElementById('val-temp').innerText = `${d.environment.temperature.toFixed(1)}°C`;
        document.getElementById('val-humid').innerText = `${d.environment.humidity.toFixed(0)}%`;
        document.getElementById('val-light').innerText = `${d.environment.light_percent.toFixed(0)}%`;
        document.getElementById('bar-light').style.width = `${d.environment.light_percent}%`;
        document.getElementById('val-vib').innerText = d.mpu.vibration_rms.toFixed(3);
        document.getElementById('val-tilt').innerText = `${d.mpu.tilt_angle.toFixed(1)}°`;
        document.getElementById('val-rpm').innerText = d.motor.rpm;
        document.getElementById('val-lat').innerText = d.gps.latitude.toFixed(6);
        document.getElementById('val-long').innerText = d.gps.longitude.toFixed(6);
        document.getElementById('val-zone').innerText = d.gps.geo_zone;
        document.getElementById('val-sats').innerText = d.gps.satellites;
        document.getElementById('val-risk').innerText = d.system.risk_score;
        document.getElementById('risk-progress').style.width = `${d.system.risk_score}%`;
        document.getElementById('val-blocked-reason').innerText = d.system.blocked_reason;
        
        // Connectivity Status
        const connTag = document.getElementById('conn-tag');
        connTag.className = "flex items-center gap-2 text-emerald-400 font-black";
        connTag.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 status-pulse"></span> LINK_ACTIVE`;

        // Risk Level Coloring
        const statusText = document.getElementById('risk-status');
        const readiness = document.getElementById('sys-readiness');
        
        if (d.system.risk_level === 'SAFE') {
            readiness.className = "px-8 py-2 glass rounded-2xl border-l-4 border-l-emerald-500 flex items-center gap-6 shadow-xl";
            statusText.className = "font-black text-xl text-emerald-400 uppercase tracking-tighter neon-text";
            statusText.innerText = "SAFE_TO_FLY";
        } else if (d.system.risk_level === 'CAUTION') {
            readiness.className = "px-8 py-2 glass rounded-2xl border-l-4 border-l-amber-500 flex items-center gap-6 shadow-xl";
            statusText.className = "font-black text-xl text-amber-500 uppercase tracking-tighter neon-text";
            statusText.innerText = "CAUTION";
        } else {
            readiness.className = "px-8 py-2 glass rounded-2xl border-l-4 border-l-rose-500 flex items-center gap-6 shadow-xl";
            statusText.className = "font-black text-xl text-rose-500 uppercase tracking-tighter neon-text";
            statusText.innerText = "ABORT";
        }

        // Active States
        document.getElementById('scan-indicator').classList.toggle('hidden', !d.system.scan_triggered);
        document.getElementById('fan-icon').classList.toggle('spin-slow', d.motor.rpm > 500);
        document.getElementById('clock').innerText = new Date().toLocaleTimeString('en-GB', { hour12: false });

        // Chart Update
        history.ax.push(d.mpu.ax);
        history.ay.push(d.mpu.ay);
        history.az.push(d.mpu.az);
        if (history.ax.length > MAX_DATAPOINTS) {
            history.ax.shift(); history.ay.shift(); history.az.shift();
        }
        chart.updateSeries([{ data: history.ax }, { data: history.ay }, { data: history.az }]);

    } catch (err) {
        document.getElementById('conn-tag').innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500"></span> OFFLINE`;
    }
}

setInterval(sync, 1000);
sync();
addLog("INIT", "AeroGuard Risk Engine Sync Complete");
