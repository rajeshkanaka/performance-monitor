#!/usr/bin/env python3

"""
performance_monitor.py

A script to monitor system performance metrics (CPU, Memory, Disk, Network, Load Average)
and generate a concise summary report as well as a visual HTML report.

Usage:
  python3 performance_monitor.py --duration 15

By default, it runs for 15 minutes if --duration is not specified.
"""

import argparse
import time
import psutil
import subprocess
import datetime
import matplotlib
import matplotlib.pyplot as plt
import os
import statistics

# For Debian systems without a display environment, use a non-interactive backend
matplotlib.use('Agg')

def get_load_average():
    """
    Return the system load average (1, 5, 15 minutes).
    On Linux, psutil.getloadavg() provides the same values as 'uptime' or 'w'.
    """
    try:
        return psutil.getloadavg()
    except AttributeError:
        # If the platform does not support getloadavg, return triple zero
        return (0, 0, 0)

def collect_metrics(interval=5):
    """
    Collect and return a dictionary of system metrics:
    CPU%, memory usage, swap usage, disk usage, network I/O, and load average.
    - interval is the time in seconds to wait for CPU measurement
    """
    # CPU usage over the specified interval
    cpu_usage = psutil.cpu_percent(interval=interval)

    # Memory usage
    mem = psutil.virtual_memory()
    memory_usage = mem.percent
    total_memory = mem.total
    used_memory = mem.used

    # Swap usage
    swap = psutil.swap_memory()
    swap_usage = swap.percent
    total_swap = swap.total
    used_swap = swap.used

    # Disk usage
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    total_disk = disk.total
    used_disk = disk.used

    # Network I/O
    net = psutil.net_io_counters()
    bytes_sent = net.bytes_sent
    bytes_recv = net.bytes_recv

    # Load average (1, 5, 15 min)
    load1, load5, load15 = get_load_average()

    metrics = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'total_memory': total_memory,
        'used_memory': used_memory,
        'swap_usage': swap_usage,
        'total_swap': total_swap,
        'used_swap': used_swap,
        'disk_usage': disk_usage,
        'total_disk': total_disk,
        'used_disk': used_disk,
        'bytes_sent': bytes_sent,
        'bytes_recv': bytes_recv,
        'load1': load1,
        'load5': load5,
        'load15': load15
    }
    return metrics

def format_bytes(size):
    """
    Format bytes to a human-readable format.
    """
    # 2**10 = 1024
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def generate_html_report(timestamps, cpu_data, mem_data, swap_data, disk_data, net_sent_data, net_recv_data, load_data):
    """
    Generate an HTML file with embedded charts of CPU, Memory, Disk, and Network usage over time.
    Also provide a text summary in the HTML.
    """
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = f"performance_report_{timestamp_str}.html"

    # Plot CPU usage
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, cpu_data, label='CPU Usage (%)', color='blue')
    plt.title("CPU Usage Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("CPU Usage (%)")
    plt.legend()
    plt.grid(True)
    cpu_chart = f"cpu_chart_{timestamp_str}.png"
    plt.savefig(cpu_chart)
    plt.close()

    # Plot Memory usage
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, mem_data, label='Memory Usage (%)', color='green')
    plt.title("Memory Usage Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Memory Usage (%)")
    plt.legend()
    plt.grid(True)
    mem_chart = f"mem_chart_{timestamp_str}.png"
    plt.savefig(mem_chart)
    plt.close()

    # Plot Disk usage
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, disk_data, label='Disk Usage (%)', color='red')
    plt.title("Disk Usage Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Disk Usage (%)")
    plt.legend()
    plt.grid(True)
    disk_chart = f"disk_chart_{timestamp_str}.png"
    plt.savefig(disk_chart)
    plt.close()

    # Plot Network usage (sent & recv) as lines
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, net_sent_data, label='Bytes Sent', color='purple')
    plt.plot(timestamps, net_recv_data, label='Bytes Received', color='orange')
    plt.title("Network I/O Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Bytes")
    plt.legend()
    plt.grid(True)
    net_chart = f"net_chart_{timestamp_str}.png"
    plt.savefig(net_chart)
    plt.close()

    # Plot load average (just for reference, let's do load1)
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, [ld[0] for ld in load_data], label='Load Average (1 min)', color='brown')
    plt.title("Load Average (1 min) Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Load Average (1 min)")
    plt.legend()
    plt.grid(True)
    load_chart = f"load_chart_{timestamp_str}.png"
    plt.savefig(load_chart)
    plt.close()

    # Convert images to base64 data URIs so we can embed them in HTML
    import base64

    def img_to_base64(img_file):
        with open(img_file, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    cpu_img_b64 = img_to_base64(cpu_chart)
    mem_img_b64 = img_to_base64(mem_chart)
    disk_img_b64 = img_to_base64(disk_chart)
    net_img_b64 = img_to_base64(net_chart)
    load_img_b64 = img_to_base64(load_chart)

    # Clean up the image files (optional)
    os.remove(cpu_chart)
    os.remove(mem_chart)
    os.remove(disk_chart)
    os.remove(net_chart)
    os.remove(load_chart)

    # Build the HTML content
    html_content = f"""
    <html>
    <head>
        <title>Performance Report - {timestamp_str}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            h1 {{
                color: #2C3E50;
            }}
            .chart {{
                margin-bottom: 40px;
            }}
            .chart img {{
                max-width: 800px;
                border: 1px solid #ccc;
                padding: 10px;
            }}
            table {{
                border-collapse: collapse;
                margin: 20px 0;
            }}
            table, th, td {{
                border: 1px solid #999;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #eee;
            }}
        </style>
    </head>
    <body>
        <h1>Performance Monitoring Report</h1>
        <div class="chart">
            <h2>CPU Usage Over Time</h2>
            <img src="data:image/png;base64,{cpu_img_b64}" alt="CPU Usage Over Time" />
        </div>
        <div class="chart">
            <h2>Memory Usage Over Time</h2>
            <img src="data:image/png;base64,{mem_img_b64}" alt="Memory Usage Over Time" />
        </div>
        <div class="chart">
            <h2>Disk Usage Over Time</h2>
            <img src="data:image/png;base64,{disk_img_b64}" alt="Disk Usage Over Time" />
        </div>
        <div class="chart">
            <h2>Network I/O Over Time</h2>
            <img src="data:image/png;base64,{net_img_b64}" alt="Network I/O Over Time" />
        </div>
        <div class="chart">
            <h2>Load Average Over Time (1 min)</h2>
            <img src="data:image/png;base64,{load_img_b64}" alt="Load Average Over Time" />
        </div>
    </body>
    </html>
    """

    # Write HTML file
    with open(html_filename, 'w') as f:
        f.write(html_content)

    print(f"\nHTML report generated: {html_filename}")

def main():
    parser = argparse.ArgumentParser(description="Performance Monitoring Script")
    parser.add_argument("--duration", type=int, default=2,
                        help="Duration in minutes to run the monitoring (default: 2).")
    parser.add_argument("--interval", type=int, default=5,
                        help="Interval in seconds between metric collections (default: 5).")
    args = parser.parse_args()

    duration_minutes = args.duration
    interval_seconds = args.interval

    print(f"Starting performance monitoring for {duration_minutes} minute(s).")
    print(f"Metrics will be collected every {interval_seconds} second(s).")

    # Calculate how many intervals we'll collect (approx)
    total_seconds = duration_minutes * 60
    iterations = int(total_seconds / interval_seconds)

    timestamps = []
    cpu_data = []
    mem_data = []
    swap_data = []
    disk_data = []
    net_sent_data = []
    net_recv_data = []
    load_data = []

    start_time = time.time()

    # Collect metrics in a loop
    for i in range(iterations):
        elapsed = time.time() - start_time
        timestamps.append(round(elapsed, 2))

        metrics = collect_metrics(interval=interval_seconds)
        cpu_data.append(metrics['cpu_usage'])
        mem_data.append(metrics['memory_usage'])
        swap_data.append(metrics['swap_usage'])
        disk_data.append(metrics['disk_usage'])
        net_sent_data.append(metrics['bytes_sent'])
        net_recv_data.append(metrics['bytes_recv'])
        load_data.append((metrics['load1'], metrics['load5'], metrics['load15']))

        # Print a brief live update
        print(f"[{i+1}/{iterations}] CPU: {metrics['cpu_usage']}%, "
              f"Mem: {metrics['memory_usage']}%, "
              f"Disk: {metrics['disk_usage']}%, "
              f"Load(1min): {metrics['load1']:.2f}")

    # Summary calculations
    avg_cpu = statistics.mean(cpu_data) if cpu_data else 0
    max_cpu = max(cpu_data) if cpu_data else 0

    avg_mem = statistics.mean(mem_data) if mem_data else 0
    max_mem = max(mem_data) if mem_data else 0

    avg_disk = statistics.mean(disk_data) if disk_data else 0
    max_disk = max(disk_data) if disk_data else 0

    avg_swap = statistics.mean(swap_data) if swap_data else 0
    max_swap = max(swap_data) if swap_data else 0

    # final message
    print("\n=== Performance Monitoring Summary ===")
    print(f"Monitoring Duration     : {duration_minutes} minute(s)")
    print(f"CPU Usage  - Avg / Max : {avg_cpu:.2f}% / {max_cpu:.2f}%")
    print(f"Memory Usage - Avg/Max : {avg_mem:.2f}% / {max_mem:.2f}%")
    print(f"Disk Usage  - Avg / Max: {avg_disk:.2f}% / {max_disk:.2f}%")
    print(f"Swap Usage  - Avg / Max: {avg_swap:.2f}% / {max_swap:.2f}%")

    # Generate HTML report with charts
    generate_html_report(timestamps, cpu_data, mem_data, swap_data, disk_data,
                         net_sent_data, net_recv_data, load_data)

    print("Monitoring complete. Please open the HTML report for visual analysis.")

if __name__ == "__main__":
    main()