import struct, socket, base64, json, sys, threading, os, subprocess, time, requests
from pymongo import MongoClient
import colorama

# MongoDB setup
client = MongoClient("mongodb+srv://siresirol937:t8gY9FXLV3JcfQ4P@cluster0.rabuteq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["mcscanner"]
scanned_servers_set = set()

working_cracked = []
scanned_ips = []

# Colors
class color:
    white = colorama.Fore.WHITE
    green = colorama.Fore.LIGHTGREEN_EX
    red = colorama.Fore.LIGHTRED_EX
    magenta = colorama.Fore.LIGHTMAGENTA_EX
    blue = colorama.Fore.LIGHTBLUE_EX

# Check for cracked server
def is_cracked(server_data):
    desc = server_data.get('description')
    if isinstance(desc, dict):
        desc = desc.get('text', '')
    if not desc:
        desc = str(server_data.get('description', ''))

    keywords = ["cracked", "offline", "no premium", "non-premium", "sem premium"]
    for kw in keywords:
        if kw.lower() in desc.lower():
            return True

    if server_data.get("enforcesSecureChat") is False:
        return True

    return False

# Ping server
def ping(ip, port=25565):
    def read_var_int(sock):
        i = 0
        j = 0
        while True:
            k = sock.recv(1)
            if not k:
                return 0
            k = k[0]
            i |= (k & 0x7f) << (j * 7)
            j += 1
            if j > 5:
                raise ValueError('var_int too big')
            if not (k & 0x80):
                return i

    sock = socket.socket()
    sock.settimeout(2)
    try:
        sock.connect((ip, port))
    except:
        return None

    try:
        host = ip.encode('utf-8')
        data = b''
        data += b'\x00'
        data += b'\x04'
        data += struct.pack('>b', len(host)) + host
        data += struct.pack('>H', port)
        data += b'\x01'
        data = struct.pack('>b', len(data)) + data
        sock.sendall(data + b'\x01\x00')
        length = read_var_int(sock)
        if length < 10:
            return None
        sock.recv(1)
        length = read_var_int(sock)
        data = b''
        while len(data) != length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return json.loads(data)
    finally:
        sock.close()

# Save to MongoDB
def save_cracked(ip, port, data):
    key = f"{ip}:{port}"
    if key in scanned_servers_set:
        return
    scanned_servers_set.add(key)
    db.servers.insert_one({
        "ip": ip,
        "port": port,
        "description": data.get('description'),
        "version": data.get('version', {}).get('name'),
        "players": str(data.get('players')),
        "protocol": data.get('version', {}).get('protocol'),
        "cracked": True
    })
    print(f"{color.green}[+] Saved cracked server: {ip}:{port}")

# Check IP
def check_ip(ip, port):
    try:
        scanned_ips.append(ip)
        data = ping(ip, port)
        if data and is_cracked(data):
            working_cracked.append(ip)
            print(f"{color.green}[CRACKED] {ip}:{port} | {data.get('version', {}).get('name')}")
            save_cracked(ip, port, data)
    except:
        pass

# Threaded scan
def scan_ips(ips, port):
    for ip in ips:
        check_ip(ip, port)

# Clear
os.system("clear")
print(colorama.Fore.LIGHTCYAN_EX + "STEIN CRACKED SERVER SCANNER\n")

# Input and resolve
raw_input_ip = input(f"{color.green}[>] Enter IP or Domain: {color.white}")
try:
    if not raw_input_ip.replace('.', '').isdigit():
        response = requests.get(f"https://api.mcsrvstat.us/3/{raw_input_ip}")
        info = response.json()
        base_ip = info["ip"]
        port = info.get("port", 25565)
    else:
        base_ip = raw_input_ip.split(":")[0]
        port = int(raw_input_ip.split(":")[1]) if ":" in raw_input_ip else 25565
except Exception as e:
    print(f"{color.red}[!] Failed to resolve domain: {e}")
    sys.exit(1)

parts = base_ip.split(".")
if len(parts) != 4:
    print(f"{color.red}Invalid IP format")
    sys.exit(1)

node = ".".join(parts[:3])
print(f"{color.blue}[*] Starting scan in subnet: {node}.0/24 on port {port}")

# Generate IP range
ip_list = [f"{node}.{i}" for i in range(1, 256)]
chunk_size = len(ip_list) // 10
ip_chunks = [ip_list[i:i + chunk_size] for i in range(0, len(ip_list), chunk_size)]

# Start scanning
start_time = time.time()
threads = []
for chunk in ip_chunks:
    t = threading.Thread(target=scan_ips, args=(chunk, port))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

end_time = time.time()

print(f"\n{color.green}Scan complete! Found {len(working_cracked)} cracked servers.")
for ip in working_cracked:
    print(f"- {ip}")
print(f"{color.white}Scanned {len(scanned_ips)} IPs in {end_time - start_time:.2f} seconds.")

input("\nPress Enter to exit...")
