# Subslasher

![banner](https://img.shields.io/badge/Subdomain-Enumerator-blueviolet?style=for-the-badge) ![python](https://img.shields.io/badge/Made%20with-Python-FFD43B?style=for-the-badge&logo=python) ![license](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> ⚔️ *Subslasher* is a powerful OSINT-based subdomain enumerator that uses `crt.sh`, SecurityTrails API, Google Dorks, and DuckDuckGo to find exposed subdomains recursively.

---

## 💡 Features

- 🔍 **Multisource Enumeration** (CRT.sh, SecurityTrails, Google Dorking, DuckDuckGo)
- 🔁 **Recursive Subdomain Hunting**
- 🔑 **API Key Rotation** (SecurityTrails)
- 💻 **Multi-threaded Scanning**
- ✨ **Beautiful CLI banners with `rich`**

---

## 🛠 Installation

```bash
git clone https://github.com/Sanket-kumbhar/Subslasher.git
cd Subslasher
pip install -r requirements.txt






usage: subdomain_enum.py [-h] -i INPUT [-a API] [-o OUTPUT] [-t THREADS]

OSINT Subdomain Enumerator - Enumerate subdomains using crt.sh and SecurityTrails API

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file with root domains (one per line).
                        Supports wildcards (*.example.com) - will be cleaned automatically.
  -a API, --api API     File with SecurityTrails API keys (one per line).
                        Supports multiple keys for rotation and usage limits.
  -o OUTPUT, --output OUTPUT
                        Output file name.
                        If filename ends with .csv, saves results in CSV format with columns: Subdomain, Source.
                        Default is all_subdomains.txt (plain text list).
  -t THREADS, --threads THREADS
                        Number of concurrent threads (default 10)

Demo usage:
python3 subdomain_enum.py -i root_domains.txt -a api_keys.txt -o results.csv

root_domains.txt example content:
*.test.in
www.test.co.in
ac.demo.in

api_keys.txt example content:
ANOTHER-KEY-HERE

The tool will enumerate subdomains recursively up to two levels deep, using crt.sh and SecurityTrails.
API keys will be rotated and usage tracked to maximize free quota.

Example :
python3 subslasher.py -i root_domains.txt -a api_keys.txt -o output.csv -r 2 -t 10

Requirments: 
pip install requests colorama beautifulsoup4


