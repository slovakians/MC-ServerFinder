import struct
import socket
import base64
import json
import sys
import threading
import colorama
import os
import subprocess
import time
import requests
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb+srv://siresirol937:t8gY9FXLV3JcfQ4P@cluster0.rabuteq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_name = 'mcscanner'
db = client[db_name]
scanned_servers_set = set()

# Tracking variables
working_servers = []
not_working_servers = []
scanned_ips = []

# Version filter
vfilter = ""

# Color setup
class color:
    white = colorama.Fore.WHITE
    green = colorama.Fore.LIGHTGREEN_EX
    red = colorama.Fore.LIGHTRED_EX
    magenta = colorama.Fore.LIGHTMAGENTA_EX
    blue = colorama.Fore.LIGHTBLUE_EX

# Server/Player classes
class Server:
    def __init__(self, data, ip, port):
        self.ip = ip
        self.port = port
        self.description = data.get('description')
        if isinstance(self.description, dict):
            self.description = self.description['text']
        self.icon = base64.b64decode(data.get('favicon', '')[22:]) if data.get('favicon') else b''
        self.players = Players(data['players'])
        self.version = data['version']['name']
        self.protocol = data['version']['protocol']

    @staticmethod
    def getVersion(data):
        return data['version']['name']

    @staticmethod
    def getDesc(data):
        desc = data.get('description')
        return desc['text'] if isinstance(desc, dict) else desc

    @staticmethod
    def getIcon(data):
        return base64.b64decode(data.get('favicon', '')[22:]) if data.get('favicon') else b''

    @staticmethod
    def getProt(data):
        return data['version']['protocol']

    @staticmethod
    def getPlayers(data):
        return Players(data['players'])

    def __str__(self):
        return f"Server(ip={self.ip}, port={self.port}, description={self.description}, version={self.version}, players={self.players}, protocol={self.protocol})"

class Players(list):
    def __init__(self, data):
        super().__init__(Player(x) for x in data.get('sample', []))
        self.max = data['max']
        self.online = data['online']

    def __str__(self):
        return f"[{', '.join(str(x) for x in self)}, online={self.online}, max={self.max}]"

class Player:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']

    def __str__(self):
        return self.name

# Ping server
def ping(ip, port=25565):
    def read_var_int():
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
        length = read_var_int()
        if length < 10:
            return None
        sock.recv(1)
        length = read_var_int()
        data = b''
        while len(data) != length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        dtolad = json.loads(data)
        serverstring = color.blue + str(Server.getDesc(dtolad)) + color.green + " | VER: " + color.blue + str(Server.getVersion(dtolad)) + color.green + " | PLAYERS: " + color.blue + str(Server.getPlayers(dtolad)) + " | PROTOCOL: " + color.blue + str(Server.getProt(dtolad))

        if vfilter and Server.getVersion(dtolad) != vfilter:
            return None
        save_to_db(ip, port, Server.getDesc(dtolad), Server.getVersion(dtolad), Server.getPlayers(dtolad), Server.getProt(dtolad))
        return serverstring
    finally:
        sock.close()

# Save server to MongoDB
def save_to_db(ip, port, description, version, players, protocol):
    server_key = f"{ip}:{port}"
    if server_key not in scanned_servers_set:
        scanned_servers_set.add(server_key)
        db.servers.insert_one({
            'ip': ip,
            'port': port,
            'description': description,
            'version': version,
            'players': str(players),
            'protocol': protocol
        })
        print(f"Saved server {ip}:{port} to database.")

# Nmap port scan
def nmap_scan(ip, port=25565):
    command = ["nmap", "-p", str(port), "--open", ip]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode()

# IP checking function
def checkip(ip, port=25565):
    try:
        res = ping(ip, port)
        scanned_ips.append(ip)
        if res:
            working_servers.append(ip)
            print(color.blue + ip + color.white + " | " + color.green + str(res))
            nmap_result = nmap_scan(ip, port)
            if str(port) in nmap_result:
                print(f"{color.green}Port {port} is OPEN on {ip}")
            else:
                print(f"{color.red}Port {port} is CLOSED on {ip}")
        else:
            not_working_servers.append(ip)
            print(f"{color.red}{ip} is not responding.")
    except:
        pass

# Multi-threaded scanning
def scan_ips(ips, port):
    for ip in ips:
        checkip(ip, port)

# Screen clear
os.system("clear")
print(colorama.Fore.LIGHTRED_EX + "\nMADE BY SYZDARK\n\nDARK'S Minecraft ServerChecker\n")

# Input and domain resolution
ipin_raw = input(colorama.Fore.LIGHTGREEN_EX + "--------------\n| ENTER YOUR\n| IP or Domain > " + colorama.Fore.LIGHTMAGENTA_EX)

try:
    if not ipin_raw.replace('.', '').isdigit():
        print(f"{color.blue}Resolving domain: {color.white}{ipin_raw}")
        response = requests.get(f"https://api.mcsrvstat.us/3/{ipin_raw}")
        resolved_data = response.json()
        ipin = resolved_data['ip']
        port = resolved_data.get('port', 25565)
        print(f"{color.green}Resolved: {ipin}:{port}")
    else:
        ipin = ipin_raw.split(":")[0]
        port = int(ipin_raw.split(":")[1]) if ":" in ipin_raw else 25565
except Exception as e:
    print(f"{color.red}Failed to resolve domain: {e}")
    sys.exit(1)

# Node IP setup
node_parts = ipin.split('.')
if len(node_parts) == 4:
    node = '.'.join(node_parts[:-1])
else:
    print(f"{color.red}Invalid IP or unsupported domain resolution result.")
    sys.exit(1)

prefix = color.magenta + "[" + color.green + "#" + color.magenta + "]" + color.white
print(prefix + " SELECTED> " + color.red + ipin + color.white + " | NODE: " + color.blue + node)

vfilter = input(colorama.Fore.LIGHTGREEN_EX + "| Version (blank = any) > " + colorama.Fore.WHITE)

print(prefix + " STARTING SCAN...")
print(prefix + " Fetch node...")

start_time = time.time()

ips = [node + "." + str(i) for i in range(1, 256)]

print(prefix + " Starting threads")
print(prefix + " Scanning")

chunk_size = len(ips) // 10
ip_chunks = [ips[i:i + chunk_size] for i in range(0, len(ips), chunk_size)]
threads = []
for i in range(10):
    t = threading.Thread(target=scan_ips, args=(ip_chunks[i], port))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

end_time = time.time()

print(prefix + " SCAN COMPLETED!")

print(f"\n{color.green}Working Servers ({len(working_servers)}): {color.white}")
for server in working_servers:
    print(f"- {server}")

print(f"\n{color.red}Not Working Servers: {len(not_working_servers)}")
print(f"\nScanned IPs: {len(scanned_ips)}")
print(f"\nTime Taken: {end_time - start_time:.2f} seconds")

input("Press Enter to exit...")
