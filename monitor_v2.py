#!/usr/bin/env python3
import psutil
import time
import argparse
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
from html import escape
import logging
from tqdm import tqdm
import colorama
from collections import defaultdict

# Initialize colorama for cross-platform colored output
colorama.init()

# Configuration
DEFAULT_DURATION = 120  # 2 minutes in seconds
INTERVAL = 5           # Sampling interval in seconds
REPORT_DIR = "performance_reports"
THRESHOLDS = {
    'cpu_percent': 90,
    'memory_percent': 90,
    'disk_io_percent': 80,
    'load_1': (os.cpu_count() * 2),
    'load_5': (os.cpu_count() * 1.5),
    'load_15': os.cpu_count()
}

# Setup logging
def setup_logging():
    """Configure logging with custom formatting"""
    log_format = '%(asctime)s [%(levelname)s] %(message)s'
    date_format = '%H:%M:%S'
    
    # Create logger
    logger = logging.getLogger('perf_monitor')
    logger.setLevel(logging.INFO)
    
    # Create console handler with custom formatter
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(log_format, date_format)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger

# Initialize logger
logger = setup_logging()

# Error tracking
error_counts = defaultdict(int)
MAX_ERROR_REPORTS = 3  # Maximum number of times to report the same error

def log_error(error_type, message):
    """Log errors with rate limiting"""
    error_counts[error_type] += 1
    if error_counts[error_type] <= MAX_ERROR_REPORTS:
        if error_counts[error_type] == MAX_ERROR_REPORTS:
            logger.warning(f"{message} (Further similar warnings will be suppressed)")
        else:
            logger.warning(message)

def collect_metrics():
    """Collect comprehensive system metrics"""
    try:
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'load_avg': psutil.getloadavg(),
                'per_cpu': psutil.cpu_percent(interval=0.1, percpu=True)
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used,
                'swap': psutil.swap_memory().percent
            },
            'disk': {
                'io_counters': None,
                'partitions': [],
                'usage': []
            },
            'network': {
                'io_counters': None,
                'connections': None
            },
            'processes': {
                'total': len(psutil.pids()),
                'top_cpu': [],
                'top_mem': []
            }
        }

        # Safely collect disk IO counters
        try:
            metrics['disk']['io_counters'] = psutil.disk_io_counters()
        except Exception as e:
            log_error('disk_io', f"Cannot collect disk IO counters: {str(e)}")

        # Safely collect network IO counters
        try:
            metrics['network']['io_counters'] = psutil.net_io_counters()
        except Exception as e:
            log_error('network_io', f"Cannot collect network IO counters: {str(e)}")

        # Try to get network connections
        try:
            metrics['network']['connections'] = len(psutil.net_connections())
        except (psutil.AccessDenied, PermissionError):
            log_error('network_connections', "Cannot access network connection information (permission denied)")
            metrics['network']['connections'] = "Permission Denied"

        # Disk partitions and usage
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                metrics['disk']['partitions'].append({
                    'device': part.device,
                    'mountpoint': part.mountpoint,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except (PermissionError, OSError) as e:
                log_error(f'disk_usage_{part.mountpoint}', f"Cannot access disk usage for {part.mountpoint}: {str(e)}")
                continue

        # Top processes (with rate limiting)
        procs = []
        try:
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = p.info
                    info['cpu_percent'] = info.get('cpu_percent', 0.0) or 0.0
                    info['memory_percent'] = info.get('memory_percent', 0.0) or 0.0
                    procs.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                
                # Rate limiting: only collect up to 1000 processes
                if len(procs) >= 1000:
                    log_error('process_limit', "Process collection limited to 1000 processes")
                    break
        except Exception as e:
            log_error('process_collection', f"Error collecting process information: {str(e)}")

        metrics['processes']['top_cpu'] = sorted(
            procs, 
            key=lambda x: x['cpu_percent'],
            reverse=True
        )[:5]
        
        metrics['processes']['top_mem'] = sorted(
            procs, 
            key=lambda x: x['memory_percent'],
            reverse=True
        )[:5]

        return metrics
    except Exception as e:
        logger.error(f"Error collecting metrics: {str(e)}")
        raise

def generate_report(data, report_path):
    """Generate HTML report with visualizations"""
    # Create plots
    create_plots(data)
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Performance Report</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .card {{ margin-bottom: 20px; }}
            .alert {{ margin: 10px 0; }}
            img {{ max-width: 100%; height: auto; }}
            .metric-summary {{ font-size: 0.9em; }}
            .problem {{ color: #dc3545; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="my-4">Performance Analysis Report</h1>
            {generate_summary(data)}
            {generate_system_overview(data)}
            {generate_cpu_section(data)}
            {generate_memory_section(data)}
            {generate_disk_section(data)}
            {generate_network_section(data)}
            {generate_process_section(data)}
        </div>
    </body>
    </html>
    """

    with open(os.path.join(report_path, "report.html"), "w") as f:
        f.write(html_content)

def create_plots(data):
    """Create matplotlib visualizations with error handling"""
    try:
        # Ensure the report directory exists
        os.makedirs(REPORT_DIR, exist_ok=True)
        
        timestamps = [datetime.fromisoformat(d['timestamp']) for d in data]
        
        # CPU Utilization Plot
        plt.figure(figsize=(12, 6))
        try:
            cpu_percent = [d['cpu']['percent'] for d in data]
            plt.plot(timestamps, cpu_percent, label='Total CPU Usage')
            plt.title('CPU Utilization Over Time')
            plt.ylabel('Percentage (%)')
            plt.ylim(0, 100)
            plt.grid(True)
            plt.savefig(os.path.join(REPORT_DIR, 'cpu_usage.png'))
        except Exception as e:
            print(f"Warning: Failed to create CPU plot: {str(e)}")
        finally:
            plt.close()

        # Memory Usage Plot
        plt.figure(figsize=(12, 6))
        try:
            mem_percent = [d['memory']['percent'] for d in data]
            plt.plot(timestamps, mem_percent, label='Memory Usage')
            plt.title('Memory Utilization Over Time')
            plt.ylabel('Percentage (%)')
            plt.ylim(0, 100)
            plt.grid(True)
            plt.savefig(os.path.join(REPORT_DIR, 'memory_usage.png'))
        except Exception as e:
            print(f"Warning: Failed to create Memory plot: {str(e)}")
        finally:
            plt.close()
    except Exception as e:
        print(f"Error creating plots: {str(e)}")

def generate_summary(data):
    """Generate summary section with alerts"""
    problems = []
    
    # Analyze data for issues
    max_cpu = max([d['cpu']['percent'] for d in data])
    max_mem = max([d['memory']['percent'] for d in data])
    load_peaks = [max(d['cpu']['load_avg']) for d in data]
    
    if max_cpu > THRESHOLDS['cpu_percent']:
        problems.append(f"High CPU usage detected ({max_cpu}%)")
        
    if max_mem > THRESHOLDS['memory_percent']:
        problems.append(f"High Memory usage detected ({max_mem}%)")
        
    if any(l > THRESHOLDS['load_1'] for l in load_peaks):
        problems.append("High system load detected")

    alerts = ""
    if problems:
        alerts = '<div class="alert alert-danger">'
        alerts += '<h4>🚨 Critical Issues Detected:</h4><ul>'
        for p in problems:
            alerts += f'<li>{p}</li>'
        alerts += '</ul></div>'
    else:
        alerts = '<div class="alert alert-success">No critical issues detected</div>'
    
    return f"""
    <div class="row">
        <div class="col-12">
            <h2>Executive Summary</h2>
            {alerts}
        </div>
    </div>
    """

def generate_system_overview(data):
    """Generate system overview section"""
    last = data[-1]
    network_connections = last['network']['connections']
    connections_display = network_connections if isinstance(network_connections, int) else "N/A"
    
    return f"""
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">System Overview</h3>
            <div class="row metric-summary">
                <div class="col-md-4">
                    <strong>CPU Cores:</strong> {len(last['cpu']['per_cpu'])}<br>
                    <strong>Current Load Average:</strong> {last['cpu']['load_avg']}<br>
                    <strong>Max CPU Usage:</strong> {max([d['cpu']['percent'] for d in data])}%
                </div>
                <div class="col-md-4">
                    <strong>Total Memory:</strong> {format_bytes(last['memory']['total'])}<br>
                    <strong>Max Memory Usage:</strong> {max([d['memory']['percent'] for d in data])}%<br>
                    <strong>Swap Usage:</strong> {last['memory']['swap']}%
                </div>
                <div class="col-md-4">
                    <strong>Processes:</strong> {last['processes']['total']}<br>
                    <strong>Network Connections:</strong> {connections_display}<br>
                    <strong>Sample Duration:</strong> {len(data) * INTERVAL} seconds
                </div>
            </div>
        </div>
    </div>
    """

def generate_cpu_section(data):
    """Generate CPU section with visualizations"""
    return f"""
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">CPU Utilization</h3>
            <img src="cpu_usage.png" alt="CPU Usage Graph">
            <div class="row metric-summary">
                <div class="col-md-6">
                    <h5>Top CPU Processes (Last Sample)</h5>
                    {generate_process_table(data[-1]['processes']['top_cpu'], 'cpu_percent')}
                </div>
                <div class="col-md-6">
                    <h5>CPU Load Averages</h5>
                    {generate_load_avg_analysis(data)}
                </div>
            </div>
        </div>
    </div>
    """

def generate_memory_section(data):
    """Generate Memory section"""
    return f"""
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">Memory Utilization</h3>
            <img src="memory_usage.png" alt="Memory Usage Graph">
            <div class="row metric-summary">
                <div class="col-md-6">
                    <h5>Top Memory Processes (Last Sample)</h5>
                    {generate_process_table(data[-1]['processes']['top_mem'], 'memory_percent')}
                </div>
                <div class="col-md-6">
                    <h5>Memory Statistics</h5>
                    {generate_memory_stats(data[-1])}
                </div>
            </div>
        </div>
    </div>
    """

def generate_process_table(processes, sort_key):
    """Generate HTML table for processes"""
    rows = []
    for p in processes:
        rows.append(f"""
        <tr>
            <td>{p['pid']}</td>
            <td>{escape(p['name'])}</td>
            <td>{p[sort_key]:.1f}%</td>
        </tr>
        """)
    
    return f"""
    <table class="table table-sm">
        <thead>
            <tr>
                <th>PID</th>
                <th>Name</th>
                <th>%</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """

def format_bytes(size):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def generate_load_avg_analysis(data):
    """Generate load average analysis HTML"""
    last = data[-1]
    load_1, load_5, load_15 = last['cpu']['load_avg']
    
    status_1 = "🟢 Normal" if load_1 <= THRESHOLDS['load_1'] else "🔴 High"
    status_5 = "🟢 Normal" if load_5 <= THRESHOLDS['load_5'] else "🔴 High"
    status_15 = "🟢 Normal" if load_15 <= THRESHOLDS['load_15'] else "🔴 High"
    
    return f"""
    <table class="table table-sm">
        <tr>
            <td>1 min average:</td>
            <td>{load_1:.2f}</td>
            <td>{status_1}</td>
        </tr>
        <tr>
            <td>5 min average:</td>
            <td>{load_5:.2f}</td>
            <td>{status_5}</td>
        </tr>
        <tr>
            <td>15 min average:</td>
            <td>{load_15:.2f}</td>
            <td>{status_15}</td>
        </tr>
    </table>
    """

def generate_memory_stats(data):
    """Generate memory statistics HTML"""
    total = format_bytes(data['memory']['total'])
    available = format_bytes(data['memory']['available'])
    used = format_bytes(data['memory']['used'])
    
    return f"""
    <table class="table table-sm">
        <tr>
            <td>Total Memory:</td>
            <td>{total}</td>
        </tr>
        <tr>
            <td>Available Memory:</td>
            <td>{available}</td>
        </tr>
        <tr>
            <td>Used Memory:</td>
            <td>{used}</td>
        </tr>
        <tr>
            <td>Swap Usage:</td>
            <td>{data['memory']['swap']}%</td>
        </tr>
    </table>
    """

def generate_disk_section(data):
    """Generate Disk section with usage information"""
    last = data[-1]
    
    disk_rows = []
    for partition in last['disk']['partitions']:
        status = "🟢 Normal" if partition['percent'] < THRESHOLDS['disk_io_percent'] else "🔴 High"
        disk_rows.append(f"""
        <tr>
            <td>{escape(partition['mountpoint'])}</td>
            <td>{format_bytes(partition['total'])}</td>
            <td>{format_bytes(partition['used'])}</td>
            <td>{partition['percent']}% {status}</td>
        </tr>
        """)
    
    return f"""
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">Disk Usage</h3>
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Mount Point</th>
                        <th>Total</th>
                        <th>Used</th>
                        <th>Usage</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(disk_rows)}
                </tbody>
            </table>
        </div>
    </div>
    """

def generate_network_section(data):
    """Generate Network section with IO statistics"""
    last = data[-1]
    io = last['network']['io_counters']
    
    return f"""
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">Network Statistics</h3>
            <div class="row metric-summary">
                <div class="col-md-6">
                    <table class="table table-sm">
                        <tr>
                            <td>Bytes Sent:</td>
                            <td>{format_bytes(io.bytes_sent)}</td>
                        </tr>
                        <tr>
                            <td>Bytes Received:</td>
                            <td>{format_bytes(io.bytes_recv)}</td>
                        </tr>
                        <tr>
                            <td>Packets Sent:</td>
                            <td>{io.packets_sent:,}</td>
                        </tr>
                        <tr>
                            <td>Packets Received:</td>
                            <td>{io.packets_recv:,}</td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <table class="table table-sm">
                        <tr>
                            <td>Active Connections:</td>
                            <td>{last['network']['connections']}</td>
                        </tr>
                        <tr>
                            <td>Errors In:</td>
                            <td>{io.errin:,}</td>
                        </tr>
                        <tr>
                            <td>Errors Out:</td>
                            <td>{io.errout:,}</td>
                        </tr>
                        <tr>
                            <td>Drops:</td>
                            <td>{io.dropin + io.dropout:,}</td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
    </div>
    """

def generate_process_section(data):
    """Generate Process section with top CPU and memory consumers"""
    last = data[-1]
    return f"""
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">Process Information</h3>
            <div class="row">
                <div class="col-md-6">
                    <h5>Top CPU Consumers</h5>
                    {generate_process_table(last['processes']['top_cpu'], 'cpu_percent')}
                </div>
                <div class="col-md-6">
                    <h5>Top Memory Consumers</h5>
                    {generate_process_table(last['processes']['top_mem'], 'memory_percent')}
                </div>
            </div>
        </div>
    </div>
    """

def cleanup_old_reports():
    """Cleanup old reports, keeping only the last 5"""
    try:
        if not os.path.exists(REPORT_DIR):
            return
            
        reports = []
        for f in os.listdir(REPORT_DIR):
            if f.endswith('.html'):
                path = os.path.join(REPORT_DIR, f)
                reports.append((os.path.getmtime(path), path))
        
        # Keep only the last 5 reports
        reports.sort(reverse=True)
        for _, path in reports[5:]:
            try:
                os.remove(path)
            except OSError:
                continue
    except Exception as e:
        print(f"Warning: Error cleaning up old reports: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Performance Monitoring Script')
    parser.add_argument('--duration', type=int, default=DEFAULT_DURATION,
                        help='Monitoring duration in seconds (default: 120, i.e., 2 minutes)')
    parser.add_argument('--keep-reports', type=int, default=5,
                        help='Number of reports to keep (default: 5)')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress bar and non-essential output')
    args = parser.parse_args()

    # Create report directory
    os.makedirs(REPORT_DIR, exist_ok=True)

    # Cleanup old reports
    cleanup_old_reports()

    collected_data = []
    start_time = time.time()
    end_time = start_time + args.duration
    total_iterations = args.duration // INTERVAL

    logger.info(f"Starting performance monitoring for {args.duration} seconds")
    logger.info(f"Reports will be saved in: {os.path.abspath(REPORT_DIR)}")
    
    try:
        with tqdm(total=total_iterations, disable=args.quiet, 
                 desc="Collecting metrics", unit="sample") as pbar:
            while time.time() < end_time:
                try:
                    metrics = collect_metrics()
                    collected_data.append(metrics)
                    remaining = end_time - time.time()
                    if remaining > 0:
                        sleep_time = min(INTERVAL, remaining)
                        time.sleep(max(0, sleep_time - (time.time() % sleep_time)))
                    pbar.update(1)
                except Exception as e:
                    logger.error(f"Error collecting metrics: {str(e)}")
                    time.sleep(1)  # Prevent tight loop on repeated errors
                    continue
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped early by user")
    
    if collected_data:
        try:
            logger.info("Generating performance report...")
            create_plots(collected_data)
            generate_report(collected_data, REPORT_DIR)
            report_path = os.path.abspath(os.path.join(REPORT_DIR, 'report.html'))
            logger.info(f"Report generated successfully: {report_path}")
            
            # Try to open the report in the default browser
            try:
                import webbrowser
                webbrowser.open(f"file://{report_path}")
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
    else:
        logger.error("No data collected, cannot generate report")

if __name__ == "__main__":
    main()