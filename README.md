# 🚀 Performance Monitor

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![psutil](https://img.shields.io/badge/psutil-latest-green.svg)](https://pypi.org/project/psutil/)
[![matplotlib](https://img.shields.io/badge/matplotlib-latest-orange.svg)](https://matplotlib.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A next-level Python tool that arms your team with real-time insights into your Debian server's performance during load or stress tests. This script goes beyond typical industry standards by providing powerful data collection, intuitive data visualization, and a self-contained HTML report.

<p align="center">
  <img src="https://user-images.githubusercontent.com/your-username/your-repo/main/docs/assets/dashboard-preview.png" alt="Performance Monitor Dashboard" width="600">
</p>

## 📚 Table of Contents

- [🚀 Performance Monitor](#-performance-monitor)
  - [📚 Table of Contents](#-table-of-contents)
  - [🌟 Overview](#-overview)
  - [✨ Features](#-features)
  - [📋 Prerequisites](#-prerequisites)
  - [🛠️ Installation](#️-installation)
  - [🚀 Usage](#-usage)
    - [Basic Usage](#basic-usage)
    - [Custom Configuration](#custom-configuration)
  - [⚙️ Configuration](#️-configuration)
  - [📊 Report Generation](#-report-generation)
    - [1. Console Summary](#1-console-summary)
    - [2. HTML Report](#2-html-report)
    - [Report Components](#report-components)
  - [📈 Performance Insights](#-performance-insights)
    - [Key Metrics Analysis](#key-metrics-analysis)
  - [🔧 Advanced Customizations](#-advanced-customizations)
  - [❓ FAQ](#-faq)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)

## 🌟 Overview

This Performance Monitoring Script is designed to empower you during critical performance or stress tests. By default, the script runs for 15 minutes and collects a snapshot of system metrics every 5 seconds, providing:

- 📊 A console summary with average and peak resource usage
- 📈 A detailed, self-contained HTML report with dynamically generated charts
- 🔍 Comprehensive metrics including CPU, Memory, Disk, Network, and Load averages

## ✨ Features

- 🔄 Cross-platform data collection using `psutil` (optimized for Debian/Linux)
- 📝 Real-time logging of system metrics
- ⚙️ Configurable duration and interval for metric collection
- 📊 Beautiful HTML report with embedded charts
- 🧹 Automatic cleanup of temporary files

## 📋 Prerequisites

1. Python 3.6+
2. System packages:

   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip -y
   ```

3. Python dependencies:
   ```bash
   pip3 install psutil matplotlib
   ```

## 🛠️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/performance-monitor.git
   cd performance-monitor
   ```

2. Make the script executable:
   ```bash
   chmod +x monitor.py
   ```

## 🚀 Usage

### Basic Usage

```bash
./monitor.py
```

### Custom Configuration

```bash
python3 monitor.py --duration 10 --interval 2
```

> 💡 **Pro Tip**: Launch this script right before starting your performance test for comprehensive metrics during the entire test duration.

## ⚙️ Configuration

| Option       | Description                         | Default |
| ------------ | ----------------------------------- | ------- |
| `--duration` | Monitoring duration in minutes      | 15      |
| `--interval` | Data collection interval in seconds | 5       |

## 📊 Report Generation

The script generates two types of reports:

### 1. Console Summary

- Real-time display of average and peak usage metrics
- Instant visibility of system performance

### 2. HTML Report

- 📈 Interactive charts for all metrics
- 🔗 Self-contained file with embedded base64 images
- 📅 Timestamp-based naming: `performance_report_YYYYMMDD_HHMMSS.html`

### Report Components

| Metric       | Description                                   |
| ------------ | --------------------------------------------- |
| CPU Usage    | Line chart showing CPU utilization percentage |
| Memory Usage | RAM consumption patterns                      |
| Disk Usage   | Storage utilization trends                    |
| Network I/O  | Bytes sent/received over time                 |
| Load Average | System load metrics                           |

## 📈 Performance Insights

### Key Metrics Analysis

| Metric  | Warning Signs     | Potential Issues      |
| ------- | ----------------- | --------------------- |
| CPU     | > 80% average     | CPU contention        |
| Memory  | High swap usage   | Memory leaks          |
| Disk    | 100% utilization  | I/O bottlenecks       |
| Network | Sudden spikes     | Bandwidth constraints |
| Load    | Exceeds CPU cores | System overload       |

## 🔧 Advanced Customizations

1. **Per-Process Monitoring**

   ```python
   for proc in psutil.process_iter():
       print(proc.name(), proc.cpu_percent())
   ```

2. **Remote Export**
   ```python
   # Example: Export to time-series DB
   def export_metrics(metrics):
       # Your export logic here
       pass
   ```

## ❓ FAQ

<details>
<summary>Does it require root privileges?</summary>
No, psutil can capture system-wide metrics without root access.
</details>

<details>
<summary>What's the performance impact?</summary>
Minimal. The script is optimized for low overhead.
</details>

<details>
<summary>Can I decrease the sampling interval?</summary>
Yes, use --interval 1 for second-by-second monitoring.
</details>

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
Made with ❤️ by Rajeshkanaka
</p>


