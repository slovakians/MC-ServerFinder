---
# 🧠 MC-ServerFinder

A powerful, multithreaded Minecraft server scanner that locates servers by scanning IPv4 subnets and filtering them by version or mode (cracked/online). Results are optionally stored in MongoDB.

> Made by SYZDARK

---

## 💡 Features

- 🌐 Scans full `/24` subnets for Minecraft servers  
- 🚀 Fast, multithreaded scanning  
- 🧩 Filters by Minecraft version  
- 🔓 Detects **cracked** (offline-mode) servers  
- 🗃️ MongoDB integration for storing results  
- 🎨 Color-coded CLI with rich output  
- 🌍 Domain/IP resolution with API fallback  
- 🧪 Nmap port scanning (optional)  

---

## 📖 Installation & Usage Tutorial

### ✅ 1. Install Python

Download Python 3.8+ from the official site:

- Windows/macOS/Linux: https://www.python.org/downloads/

✅ Make sure to **check "Add Python to PATH"** during installation.

---

### ✅ 2. Clone the Repository

```bash
git clone https://github.com/slovakians/MC-ServerFinder
cd MC-ServerFinder
````

---

### ✅ 3. Install Required Python Packages

Use pip to install dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing, just run:

```bash
pip install colorama pymongo requests
```

---

### ✅ 4. (Optional) Install Nmap

If you want port scanning functionality:

* **Windows**: [https://nmap.org/download.html](https://nmap.org/download.html)
* **Linux/macOS**:

```bash
sudo apt install nmap        # Debian/Ubuntu
brew install nmap            # macOS
```

---

### 🧠 Python Scripts

#### ▶️ `mcscanner.py` — Full subnet scanner

Scans a subnet for Minecraft servers and logs all valid results.

```bash
python mcscanner.py
```

You will be prompted for:

* A domain or IP address
* A version filter (optional)

---

#### 🔓 `cracked_scanner.py` — Cracked server scanner

Specifically detects **offline-mode (cracked)** servers.

```bash
python cracked_scanner.py
```

Only logs cracked servers with insecure chat or missing authentication.

---

## 💾 MongoDB Setup

Make sure your MongoDB URI is configured in both scripts:

```python
client = MongoClient("mongodb+srv://<user>:<pass>@cluster0.mongodb.net/")
```

You can use **MongoDB Atlas** or a local instance.

---

## 📁 File Structure

```
MC-ServerFinder/
├── mcscanner.py            # Main server scanner
├── cracked_scanner.py      # Cracked server scanner
├── requirements.txt        # Dependencies
└── README.md               # This file
```

---

## 📜 License

MIT © slovakians / SYZDARK

---
## 🔥 INFO
this is a fast scanner that works by generating ips for example 123.90.87.120 it will remove the 120 and replace it with a random digit highest is 3 digits

and now after generating is done it will now try checking if its a mc server with the default port 25565 and its crazy fast please use the bot.py

to get the servers or find a server u want!

Find servers at [minecraft-mp.com](https://minecraft-mp.com/servers/list/12/) just copy domain paste and wait
---
