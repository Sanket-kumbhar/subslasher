# subslasher.py (Updated)

import argparse
import os
import re
import csv
import threading
import requests
import time
from urllib.parse import urlparse
from time import sleep
from bs4 import BeautifulSoup
import random

# Optional: rich formatting
try:
    from rich import print
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
except ImportError:
    console = None
    print = print

# Globals
FOUND_SUBDOMAINS = set()
LOCK = threading.Lock()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0'
}

BANNERS = [
    r"""
  ██████ ▓█████ █     █░ ██▓     ▄▄▄       ███▄    █ ▓█████ ▄▄▄      
▒██    ▒ ▓█   ▀▓█░ █ ░█░▓██▒    ▒████▄     ██ ▀█   █ ▓█   ▀▒████▄    
░ ▓██▄   ▒███  ▒█░ █ ░█ ▒██░    ▒██  ▀█▄  ▓██  ▀█ ██▒▒███  ▒██  ▀█▄  
  ▒   ██▒▒▓█  ▄░█░ █ ░█ ▒██░    ░██▄▄▄▄██ ▓██▒  ▐▌██▒▒▓█  ▄░██▄▄▄▄██ 
▒██████▒▒░▒████░░░▒░░▒░ ░██████▒ ▓█   ▓██▒▒██░   ▓██░░▒████▒▓█   ▓██▒
▒ ▒▓▒ ▒ ░░░ ▒░ ░░░ ░ ░  ░ ▒░▓  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░░ ▒░ ░▒▒   ▓▒█░
░ ░▒  ░ ░ ░ ░  ░  ░     ░ ░ ▒  ░  ▒   ▒▒ ░░ ░░   ░ ▒░ ░ ░  ░ ▒   ▒▒ ░
░  ░  ░     ░   ░         ░ ░     ░   ▒      ░   ░ ░    ░    ░   ▒   
      ░     ░  ░              ░  ░      ░  ░         ░  ░     ░  ░  
                                                                    
          Subslasher - OSINT Subdomain Enumerator
              by Sanket Kumbhar | github.com/Sanket-kumbhar
    """
]

# Functions

def show_banner():
    if console:
        banner = random.choice(BANNERS)
        console.print(Panel.fit(banner, title="[bold neon_green]Subslasher[/bold neon_green]", subtitle="by [bold blue]Sanket Kumbhar[/bold blue] • github.com/Sanket-kumbhar", border_style="green"))

def load_domains(file_path):
    with open(file_path, 'r') as f:
        return [line.strip().replace('*.','') for line in f if line.strip()]

def load_api_keys(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def crtsh_enum(domain):
    try:
        response = requests.get(f"https://crt.sh/?q=%25.{domain}&output=json", headers=HEADERS, timeout=10)
        if response.ok:
            entries = response.json()
            with LOCK:
                for entry in entries:
                    name = entry.get("name_value")
                    if name:
                        for sub in name.split('\n'):
                            FOUND_SUBDOMAINS.add((sub.strip(), "crt.sh"))
    except Exception:
        pass

def securitytrails_enum(domain, api_keys):
    key_index = 0
    total_keys = len(api_keys)
    headers = {"Content-Type": "application/json"}

    while key_index < total_keys:
        key = api_keys[key_index]
        headers["APIKEY"] = key

        try:
            response = requests.get(f"https://api.securitytrails.com/v1/domain/{domain}/subdomains", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                subs = data.get("subdomains", [])
                with LOCK:
                    for sub in subs:
                        FOUND_SUBDOMAINS.add((f"{sub}.{domain}", "SecurityTrails"))
                return
            elif response.status_code == 429:
                key_index += 1
                continue
            else:
                break
        except:
            key_index += 1
            continue

def google_dork_enum(domain):
    queries = [
        f"site:{domain} -www",
        f"inurl:{domain}"
    ]
    for query in queries:
        try:
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and 'url?q=' in href:
                    match = re.search(r'url\?q=(https?://[^&]+)', href)
                    if match:
                        parsed = urlparse(match.group(1))
                        if parsed.hostname and domain in parsed.hostname:
                            FOUND_SUBDOMAINS.add((parsed.hostname, "Google Dork"))
        except:
            continue

def duckduckgo_search(domain):
    try:
        url = f"https://html.duckduckgo.com/html/?q=site:{domain}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            parsed = urlparse(href)
            if parsed.hostname and domain in parsed.hostname:
                FOUND_SUBDOMAINS.add((parsed.hostname, "DuckDuckGo"))
    except:
        pass

def recurse_subdomains(subdomain, depth):
    parts = subdomain.split('.')
    if len(parts) > depth:
        parent = '.'.join(parts[1:])
        crtsh_enum(parent)
        google_dork_enum(parent)
        duckduckgo_search(parent)

# CLI setup
parser = argparse.ArgumentParser(
    prog="Subslasher",
    description=r"""
Subslasher - OSINT Subdomain Enumerator & Dork Scraper
Enumerate subdomains recursively using multiple methods, with API key rotation.
Created by Sanket Kumbhar (https://github.com/Sanket-kumbhar)
""",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument("-i", "--input", required=True, help="Input file with root domains")
parser.add_argument("-a", "--api", help="API key file for SecurityTrails")
parser.add_argument("-o", "--output", default="all_subdomains.txt", help="Output file (.csv or .txt)")
parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads")
parser.add_argument("-r", "--recursion", type=int, default=2, help="Recursion depth")
parser.add_argument("--no-crtsh", action="store_true", help="Disable crt.sh")
parser.add_argument("--no-st", action="store_true", help="Disable SecurityTrails")
parser.add_argument("--no-googledork", action="store_true", help="Disable Google Dorks")
parser.add_argument("--no-websearch", action="store_true", help="Disable Web Search")
parser.epilog = r"""
Example:
  python3 subslasher.py -i domains.txt -a apis.txt -o output.csv
"""
args = parser.parse_args()

THREADS = args.threads

show_banner()

# Load
root_domains = load_domains(args.input)
api_keys = load_api_keys(args.api) if args.api else []

# Execution
threads = []

for domain in root_domains:
    if not args.no_crtsh:
        threads.append(threading.Thread(target=crtsh_enum, args=(domain,)))
    if not args.no_st and api_keys:
        threads.append(threading.Thread(target=securitytrails_enum, args=(domain, api_keys)))
    if not args.no_googledork:
        threads.append(threading.Thread(target=google_dork_enum, args=(domain,)))
    if not args.no_websearch:
        threads.append(threading.Thread(target=duckduckgo_search, args=(domain,)))

# Launch threads
for t in threads:
    t.start()
    while threading.active_count() > THREADS:
        sleep(0.1)

for t in threads:
    t.join()

# Recursively dig subdomains
for sub, _ in list(FOUND_SUBDOMAINS):
    recurse_subdomains(sub, args.recursion)

# Save Output
if args.output.endswith(".csv"):
    with open(args.output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Subdomain", "Source"])
        for sub, source in sorted(FOUND_SUBDOMAINS):
            writer.writerow([sub, source])
else:
    with open(args.output, 'w') as f:
        for sub, source in sorted(FOUND_SUBDOMAINS):
            f.write(f"{sub} ({source})\n")

if console:
    console.print(f"[bold green]\nDone. Found {len(FOUND_SUBDOMAINS)} unique subdomains. Saved to {args.output}.[/bold green]")
else:
    print(f"\nDone. Found {len(FOUND_SUBDOMAINS)} unique subdomains. Saved to {args.output}.")
