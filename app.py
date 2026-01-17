from flask import Flask, request

app = Flask(__name__)
latest_value = 0
history = []
MAX_HISTORY = 50

@app.route('/data', methods=['POST'])
def receive_data():
    global latest_value, history
    latest_value = request.json['value']
    
    # Store history
    history.append(latest_value)
    if len(history) > MAX_HISTORY:
        history.pop(0)
    
    print("Received:", latest_value)
    return "OK"

@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>D1 Mini Live Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .container {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 24px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 800px;
                width: 100%;
                backdrop-filter: blur(10px);
            }}
            
            h1 {{
                color: #2d3748;
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .subtitle {{
                text-align: center;
                color: #718096;
                margin-bottom: 40px;
                font-size: 1rem;
            }}
            
            .status {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: #48bb78;
                color: white;
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 600;
            }}
            
            .status-dot {{
                width: 8px;
                height: 8px;
                background: white;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            
            .value-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                padding: 30px;
                text-align: center;
                margin: 30px 0;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                transform: translateY(0);
                transition: transform 0.3s ease;
            }}
            
            .value-card:hover {{
                transform: translateY(-5px);
            }}
            
            .value-label {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 0.875rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
                font-weight: 600;
            }}
            
            .value {{
                color: white;
                font-size: 4rem;
                font-weight: 700;
                line-height: 1;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }}
            
            .value-unit {{
                color: rgba(255, 255, 255, 0.8);
                font-size: 1.5rem;
                margin-left: 10px;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            
            .stat-card {{
                background: #f7fafc;
                border-radius: 12px;
                padding: 20px;
                border: 2px solid #e2e8f0;
                transition: all 0.3s ease;
            }}
            
            .stat-card:hover {{
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            }}
            
            .stat-label {{
                color: #718096;
                font-size: 0.875rem;
                margin-bottom: 8px;
                font-weight: 600;
            }}
            
            .stat-value {{
                color: #2d3748;
                font-size: 1.75rem;
                font-weight: 700;
            }}
            
            .chart-container {{
                margin-top: 30px;
                padding: 20px;
                background: #f7fafc;
                border-radius: 12px;
                border: 2px solid #e2e8f0;
            }}
            
            .chart-title {{
                color: #2d3748;
                font-size: 1rem;
                font-weight: 600;
                margin-bottom: 15px;
            }}
            
            canvas {{
                max-width: 100%;
                height: 200px !important;
            }}
            
            .update-time {{
                text-align: center;
                color: #a0aec0;
                font-size: 0.875rem;
                margin-top: 20px;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    padding: 20px;
                }}
                
                h1 {{
                    font-size: 2rem;
                }}
                
                .value {{
                    font-size: 3rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚡ D1 Mini Dashboard</h1>
            <div class="subtitle">
                <span class="status">
                    <span class="status-dot"></span>
                    Live
                </span>
            </div>
            
            <div class="value-card">
                <div class="value-label">Current Reading</div>
                <div>
                    <span class="value" id="val">{latest_value}</span>
                    <span class="value-unit">ADC</span>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Min Value</div>
                    <div class="stat-value" id="min">--</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Max Value</div>
                    <div class="stat-value" id="max">--</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Average</div>
                    <div class="stat-value" id="avg">--</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📊 Real-time History</div>
                <canvas id="chart"></canvas>
            </div>
            
            <div class="update-time">
                Last updated: <span id="time">--</span>
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <script>
            const ctx = document.getElementById('chart').getContext('2d');
            const data = {{
                labels: [],
                datasets: [{{
                    label: 'Sensor Value',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }}]
            }};
            
            const chart = new Chart(ctx, {{
                type: 'line',
                data: data,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            grid: {{
                                color: '#e2e8f0'
                            }},
                            ticks: {{
                                color: '#718096'
                            }}
                        }},
                        x: {{
                            display: false
                        }}
                    }},
                    animation: {{
                        duration: 300
                    }}
                }}
            }});
            
            let values = [];
            
            function updateStats() {{
                if (values.length === 0) return;
                
                const min = Math.min(...values);
                const max = Math.max(...values);
                const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
                
                document.getElementById('min').textContent = min;
                document.getElementById('max').textContent = max;
                document.getElementById('avg').textContent = avg;
            }}
            
            setInterval(async () => {{
                try {{
                    const res = await fetch('/value');
                    const value = parseInt(await res.text());
                    
                    document.getElementById("val").textContent = value;
                    document.getElementById("time").textContent = new Date().toLocaleTimeString();
                    
                    values.push(value);
                    if (values.length > 50) values.shift();
                    
                    data.labels.push('');
                    data.datasets[0].data.push(value);
                    
                    if (data.labels.length > 50) {{
                        data.labels.shift();
                        data.datasets[0].data.shift();
                    }}
                    
                    chart.update('none');
                    updateStats();
                }} catch (e) {{
                    console.error('Error fetching data:', e);
                }}
            }}, 1000);
        </script>
    </body>
    </html>
    """

@app.route('/value')
def value():
    return str(latest_value)

app.run(host="0.0.0.0", port=5000)