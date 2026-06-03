# XSS-SCAN 🔍⚡

**Cross-Site Scripting (XSS) Vulnerability Scanner**

> Built for Kali Linux | Python 3 | Terminal Tool | Selenium Headless Chrome  
> By [UI-HACKER-india](https://github.com/UI-HACKER-india)

---

## ⚠️ Disclaimer

> **This tool is for educational purposes and authorized penetration testing only.**  
> Do NOT use on systems you do not own or do not have explicit written permission to test.  
> The author is not responsible for any misuse.

---

## 🚀 Features

- ✅ Scan **single URL** or a **file of multiple URLs**
- ✅ **Selenium Headless Chrome** — detects actual `alert()` popup (NO false positives)
- ✅ **Driver Pool** — multiple Chrome instances running in parallel (fast)
- ✅ **70+ built-in XSS payloads** — or load your own 2000+ payload file
- ✅ Injects payloads into **all GET parameters** automatically
- ✅ Color-coded terminal output — `GREEN = VULNERABLE` `RED = NOT VULNERABLE`
- ✅ Live progress bar during scan
- ✅ Captures **alert text** from confirmed XSS
- ✅ Final summary with total confirmed vulnerabilities
- ✅ Export results as **TXT**, **JSON**, or **HTML** (browser report)

---

## 🧠 How Detection Works

Most basic XSS scanners just check if the payload **appears in the HTTP response** — this causes massive false positives because many sites reflect URL parameters as plain text without executing them.

**XSS-SCAN uses a different approach — exactly like loxs:**

```
URL + Payload → Headless Chrome opens it → JavaScript executes → 
alert() fires? → YES = CONFIRMED XSS ✅  |  NO = NOT VULNERABLE ❌
```

- Uses **Selenium WebDriver** to control real Chrome browser (invisibly)
- Waits for actual `alert()` / `confirm()` / `prompt()` popup
- If popup fires → **100% confirmed XSS** (no guessing)
- If no popup → marked as **NOT VULNERABLE** (no false positives)

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/UI-HACKER-india/xss-scan.git
cd xss-scan
```

### 2. Install dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

### 3. Install Google Chrome (Kali Linux)

```bash
# Method 1 — apt
sudo apt update
sudo apt install google-chrome-stable -y

# Method 2 — if not in apt
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y
```

### 4. Give execute permission

```bash
chmod +x xss_scanner.py
```

---

## ▶️ Usage

```bash
python3 xss_scanner.py
```

The tool will interactively ask you:

```
[?] Choose [1/2]:          → Single URL or file?
[?] Choose [1/2]:          → Built-in or custom payloads?
[?] Threads [5]:           → Parallel Chrome instances
[?] Alert Timeout [3]:     → Seconds to wait for popup per payload
[?] Start scan? [Y/n]:     → Confirm and go
...scanning...
[?] Save results? [Y/n]:   → TXT / JSON / HTML
```

---

## 📸 Sample Terminal Output

```
════════════════════════════════════════════════════════════
  ▶  Scanning → https://testphp.vulnweb.com/search.php?test=query
════════════════════════════════════════════════════════════

  [*] Payloads  : 70
  [*] Threads   : 5
  [*] Method    : Selenium Headless Chrome — Real Alert Detection

  Progress [████████████████░░░░░░░░] 45/70

  [VULN ⚡] ALERT FIRED!  Payload : <script>alert(1)</script>
            Alert text : "1"

  [VULN ⚡] ALERT FIRED!  Payload : <img src=x onerror=alert(1)>
            Alert text : "1"

  [✓] Result → 2 CONFIRMED XSS found in target URL

════════════════════════════════════════════════════════════
  ▶  SCAN COMPLETE — FINAL RESULTS
════════════════════════════════════════════════════════════

  URLs Scanned        : 1
  Total Tested        : 70
  Vulnerable URLs     : 1
  Clean URLs          : 0
  Total Confirmed XSS : 2
```

---

## 📁 Project Structure

```
xss-scan/
├── xss_scanner.py      # Main scanner (Selenium based)
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── payloads/
    └── custom.txt      # (Optional) Your own payload list
```

---

## 🔧 Custom Payload File Format

One payload per line:

```
<script>alert(1)</script>
<img src=x onerror=alert(1)>
"><svg onload=alert(1)>
```

Compatible with [SecLists XSS payloads](https://github.com/danielmiessler/SecLists/tree/master/Fuzzing/XSS):

```bash
# Kali Linux pe SecLists install karo
sudo apt install seclists -y

# Path use karo tool mein
/usr/share/seclists/Fuzzing/XSS/xss-payload-list.txt
```

---

## 🧪 Legal Practice Targets

| Lab | URL |
|-----|-----|
| DVWA | `http://localhost/dvwa` |
| bWAPP | `http://localhost/bWAPP` |
| Acunetix Test | `http://testphp.vulnweb.com` |
| XSS Game | `https://xss-game.appspot.com` |
| TryHackMe / HackTheBox | Legal lab environments |

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3 |
| Browser Automation | Selenium WebDriver |
| Chrome Driver | webdriver-manager (auto install) |
| Threading | concurrent.futures ThreadPoolExecutor |
| Colors | colorama |
| Platform | Kali Linux (recommended) |

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**UI-HACKER-india**  
🎥 YouTube: [UI-HACKER-india](https://youtube.com/@UI-HACKER-india)  
🐙 GitHub: [UI-HACKER-india](https://github.com/UI-HACKER-india)

---

*Made with ❤️ for the Indian cybersecurity community*
