# 🚀 System Performance Sentinel

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![Documentation](https://img.shields.io/badge/docs-comprehensive-brightgreen)
![Test Coverage](https://img.shields.io/badge/coverage-95%25-success)
![Last Commit](https://img.shields.io/github/last-commit/yourusername/system-performance-sentinel)

> Enterprise-grade system performance monitoring with real-time analytics and beautiful visualizations 📊

<div align="center">
  <img src="perfcard01.png" alt="Performance Sentinel Banner">
</div>

## ✨ Features

### 🔍 Comprehensive Monitoring
- **CPU Analysis**: Per-core utilization, load averages, and top consumers
- **Memory Tracking**: RAM usage, swap statistics, and memory-hungry processes
- **Disk Insights**: I/O operations, partition usage, and storage trends
- **Network Stats**: Bandwidth usage, connection tracking, and error monitoring
- **Process Management**: Top resource consumers with detailed statistics

### 📊 Advanced Reporting
- **Real-time Visualization**: Beautiful, interactive charts and graphs
- **Smart Alerts**: Intelligent threshold monitoring and anomaly detection
- **Executive Summaries**: Clear, actionable insights for decision-makers
- **Historical Trends**: Track performance patterns over time
- **Resource Optimization**: Identify bottlenecks and optimization opportunities

## 🖥️ Sample Report Preview

<details>
<summary>Click to see the beautiful report output 👀</summary>

### Executive Summary
![Executive Summary](docs/report_preview/summary.png)

### System Overview
![System Overview](docs/report_preview/overview.png)

### Resource Utilization
![Resource Charts](docs/report_preview/charts.png)

</details>

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip or uv package manager
- Administrative privileges for some metrics

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/system-performance-sentinel.git
cd system-performance-sentinel

# Install using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

### Basic Usage

```bash
# Run with default settings (2 minutes monitoring)
python monitor_v2.py

# Custom duration (e.g., 1 hour)
python monitor_v2.py --duration 3600

# Quiet mode (minimal output)
python monitor_v2.py --quiet

# Specify report retention
python monitor_v2.py --keep-reports 10
```

## 📊 Output Examples

### Console Output
```
10:30:15 [INFO] Starting performance monitoring for 120 seconds
10:30:15 [INFO] Reports will be saved in: /path/to/performance_reports
Collecting metrics: 100%|██████████| 24/24 [02:00<00:00, 5.00s/sample]
10:32:15 [INFO] Generating performance report...
10:32:16 [INFO] Report generated successfully: /path/to/report.html
```

### Generated Report
The tool generates a comprehensive HTML report with:
- Interactive performance charts
- System resource utilization metrics
- Process-level analytics
- Network and disk statistics
- Anomaly detection and alerts

## 🛠️ Advanced Configuration

### Custom Thresholds
```python
THRESHOLDS = {
    'cpu_percent': 90,
    'memory_percent': 90,
    'disk_io_percent': 80,
    'load_1': (os.cpu_count() * 2),
    'load_5': (os.cpu_count() * 1.5),
    'load_15': os.cpu_count()
}
```

### Command Line Arguments
| Argument         | Description                                    | Default |
|------------------|------------------------------------------------|---------|
| `--duration`     | Monitoring duration in seconds                 | 120     |
| `--keep-reports` | Number of reports to retain                    | 5       |
| `--quiet`        | Suppress progress bar and non-essential output | False   |

## 🔧 Development

### Setting Up Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows

# Install dev dependencies
pip install -r requirements-dev.txt
```

### Running Tests
```bash
pytest tests/ -v --cov=src
```

## 📚 Documentation

Detailed documentation is available in the [docs](./docs) directory:
- [Installation Guide](./docs/installation.md)
- [Usage Examples](./docs/usage.md)
- [API Reference](./docs/api.md)
- [Contributing Guidelines](./docs/contributing.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
Made with ❤️ by Rajeshkanaka
</p>


